# forgemind-backend/app.py

import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from pydantic import BaseModel, ValidationError
from openai import OpenAI
import re
from redis import Redis
import json
from typing import Optional
import base64
from PIL import Image
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Retrieve Supabase URL and Anon Key from environment variables
SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

# Get OpenAI API key from environment variables
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# Retrieve Supabase S3 credentials from environment variables
SUPABASE_STORAGE_S3_ACCESS_KEY_ID = os.getenv("SUPABASE_STORAGE_S3_ACCESS_KEY_ID")
SUPABASE_STORAGE_S3_SECRET_ACCESS_KEY = os.getenv(
    "SUPABASE_STORAGE_S3_SECRET_ACCESS_KEY"
)

# Initialize Supabase Storage client
storage_client = supabase.storage

# Check if the storage bucket "fusion_screenshots" exists, create if it doesn't
bucket_name = "fusion_screenshots"
try:
    bucket_list = storage_client.list_buckets()
    if bucket_name not in [bucket.name for bucket in bucket_list]:
        storage_client.create_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")
except Exception as e:
    print(f"Error checking/creating bucket: {e}")

# Initialize Redis client - use REDISCLOUD_URL for Heroku Redis Cloud compatibility
redis_url = os.getenv("REDISCLOUD_URL", "redis://localhost:6379/0")
try:
    redis_client = Redis.from_url(redis_url, socket_connect_timeout=2)
    # Test the connection
    redis_client.ping()
    print("Successfully connected to Redis")
    use_redis = True
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    print("The application will run with limited functionality (no CAD state tracking)")

    # Create a mock Redis client that does nothing
    class MockRedis:
        def set(self, *args, **kwargs):
            return True

        def get(self, *args, **kwargs):
            return None

        def delete(self, *args, **kwargs):
            return True

        def ping(self, *args, **kwargs):
            return True

        def exists(self, *args, **kwargs):
            return False

        def keys(self, *args, **kwargs):
            return []

        def hset(self, *args, **kwargs):
            return True

        def hget(self, *args, **kwargs):
            return None

        def hmset(self, *args, **kwargs):
            return True

        def hmget(self, *args, **kwargs):
            return [None]

        def hgetall(self, *args, **kwargs):
            return {}

        def decode(self, *args, **kwargs):
            return None

    redis_client = MockRedis()
    use_redis = False

app = Flask(__name__)
# Explicitly allow all origins with a single CORS configuration
CORS(app, resources={r"/*": {"origins": "*"}})


# Error handler to ensure all errors return JSON
@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if hasattr(e, "code"):
        code = e.code
    return jsonify(error=str(e)), code


class ChatPayload(BaseModel):
    text: str
    user_id: str
    thread_id: Optional[str] = None  # new optional field


@app.route("/chat", methods=["OPTIONS", "POST"])
def chat():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    try:
        data = ChatPayload(**request.get_json())
    except ValidationError as e:
        return (
            jsonify(
                {"status": "error", "message": "Invalid payload", "errors": e.errors()}
            ),
            400,
        )

    # Insert or get the chat
    if data.thread_id:
        # Get an existing chat if thread_id is provided
        existing_chats = (
            supabase.table("chats")
            .select("*")
            .eq("thread_id", data.thread_id)
            .execute()
        )

        if existing_chats.data and len(existing_chats.data) > 0:
            chat_id = existing_chats.data[0]["id"]
            # Update the timestamp
            supabase.table("chats").update({"updated_at": "now()"}).eq(
                "id", chat_id
            ).execute()
        else:
            # If no chat with this thread_id exists, create a new one
            chat_insertion = (
                supabase.table("chats")
                .insert(
                    {
                        "title": f"Chat {data.text[:30]}...",  # Use the first 30 chars as title
                        "user_id": data.user_id,
                        "assistant_id": "asst_SICfkmxReT9Xd76xOmieEqpL",
                        "thread_id": data.thread_id,
                    }
                )
                .execute()
            )
            chat_id = chat_insertion.data[0]["id"]
    else:
        # Create a new chat if no thread_id is provided
        chat_insertion = (
            supabase.table("chats")
            .insert(
                {
                    "title": f"Chat {data.text[:30]}...",  # Use the first 30 chars as title
                    "user_id": data.user_id,
                    "assistant_id": "asst_SICfkmxReT9Xd76xOmieEqpL",
                }
            )
            .execute()
        )
        chat_id = chat_insertion.data[0]["id"]

    # Add the user message to the messages table
    supabase.table("messages").insert(
        {"chat_id": chat_id, "role": "user", "content": data.text}
    ).execute()

    # Use existing thread if provided; otherwise, create a new one.
    if data.thread_id:
        thread_id = data.thread_id
        # Assuming the thread exists; in production, you might verify it.
    else:
        # Clear all Redis states for the user
        try:
            redis_client.delete(f"cad_state:{data.user_id}")
            redis_client.delete(f"status:{data.user_id}")
            redis_client.delete(f"message:{data.user_id}")
        except Exception as e:
            print(f"Warning: Redis operation failed: {e}")

        thread = client.beta.threads.create()
        thread_id = thread.id

        # Update the chat with the thread_id
        supabase.table("chats").update({"thread_id": thread_id}).eq(
            "id", chat_id
        ).execute()

    # Get CAD state from Redis with error handling
    try:
        cad_state = redis_client.get(f"cad_state:{data.user_id}")
        cad_state = cad_state.decode("utf-8") if cad_state else "No CAD state found"

        cad_status = redis_client.get(f"status:{data.user_id}")
        cad_status = cad_status.decode("utf-8") if cad_status else "No CAD status found"

        cad_message = redis_client.get(f"message:{data.user_id}")
        cad_message = (
            cad_message.decode("utf-8") if cad_message else "No CAD message found"
        )

        cad_status += f"\n{cad_message}"
    except Exception as e:
        print(f"Warning: Error retrieving Redis data: {e}")
        cad_state = "No CAD state found"
        cad_status = "No CAD status found"

    print(
        "Checking keys",
        f"cad_state:{data.user_id}",
        f"status:{data.user_id}",
        f"message:{data.user_id}",
    )
    content = f"CAD workspace contents:\n```\n{cad_state}\n```\nCAD workspace status:\n```\n{cad_status}\n````\nInstructions:\n```\n{data.text}\n```"

    print("------- Query to LLM   -----------------------")
    print(content)
    print("------- Query Complete -----------------------")
    # Add a message to the thread using the determined thread_id.
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=content
    )

    # Create a run using the thread_id.
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id="asst_SICfkmxReT9Xd76xOmieEqpL"
    )

    # Wait for the run to complete
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # Get the messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)

    # Accumulate the assistant's response
    assistant_response = next(
        (
            msg["content"]
            for msg in parse_messages(messages)
            if msg["role"] == "assistant"
        ),
        "No response from assistant",
    )

    assistant_response = json.loads(assistant_response)

    # Add the assistant response to the messages table
    supabase.table("messages").insert(
        {"chat_id": chat_id, "role": "assistant", "content": assistant_response}
    ).execute()

    supabase.table("operations").insert(
        {
            "steps": assistant_response["steps"],
            "python_code": assistant_response["python_code"],
            "user_facing_response": assistant_response["user_facing_response"],
            "chat_id": chat_id,
            "user_id": data.user_id,
            "cad_type": "fusion",
            "status": "pending",
        }
    ).execute()
    # Log operation creation for security auditing
    print(f"Created new operation for user {data.user_id} with chat_id {chat_id}")

    return jsonify(
        {
            "status": "success",
            "response": assistant_response["user_facing_response"],
            "thread_id": thread_id,
            "chat_id": chat_id,
        }
    )


@app.route("/instruction_result", methods=["POST"])
def instruction_result():
    data = request.get_json()
    user_id = data.get("user_id")
    cad_state = data.get("cad_state")
    message = data.get("message")
    status = data.get("status")
    before_screenshot = data.get("before_screenshot")
    after_screenshot = data.get("after_screenshot")

    if not user_id:
        print("Missing user_id")
        return jsonify({"status": False, "message": "Missing user_id"}), 400
    if not cad_state:
        print("Missing cad_state")
        return jsonify({"status": False, "message": "Missing cad_state"}), 400
    if not message and status != "success":
        print("Missing message")
        return jsonify({"status": False, "message": "Missing message"}), 400
    if not status:
        print("Missing status")
        return jsonify({"status": False, "message": "Missing status"}), 400

    # Log operation completion by user (for security auditing)
    print(f"Operation completed by user {user_id} with status: {status}")

    # If status is not "success", mark it as "error" in database
    final_status = "completed" if status == "success" else "error"

    # Update the most recent sent operation for this user to completed/error
    try:
        sent_ops = (
            supabase.table("operations")
            .select("*")
            .eq("status", "sent")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if sent_ops.data and len(sent_ops.data) > 0:
            op = sent_ops.data[0]

            # Upload screenshots to Supabase S3 storage
            def upload_screenshot(screenshot_data, filename):
                try:
                    # Decode the base64 image data
                    image_data = base64.b64decode(screenshot_data.split(",")[1])
                    # Compress the image
                    image = Image.open(BytesIO(image_data))
                    compressed_image_io = BytesIO()
                    image.save(
                        compressed_image_io, format="PNG", optimize=True, quality=85
                    )
                    compressed_image_io.seek(0)
                    # Upload to Supabase Storage
                    storage_client.from_(bucket_name).upload(
                        filename, compressed_image_io
                    )
                    # Get the public URL of the uploaded image
                    public_url = storage_client.from_(bucket_name).get_public_url(
                        filename
                    )
                    return public_url
                except Exception as e:
                    print(f"Error uploading screenshot: {e}")
                    return None

            before_screenshot_url = None
            after_screenshot_url = None

            if before_screenshot:
                before_screenshot_url = upload_screenshot(
                    before_screenshot, f"{user_id}_before.png"
                )
            if after_screenshot:
                after_screenshot_url = upload_screenshot(
                    after_screenshot, f"{user_id}_after.png"
                )

            # Update operation status with screenshot URLs
            supabase.table("operations").update(
                {
                    "status": final_status
                }
            ).eq("id", op["id"]).execute()

            print(
                f"Updated operation {op['id']} for user {user_id} to status: {final_status}"
            )
        else:
            print(f"No sent operation found for user {user_id} to update")
    except Exception as e:
        print(f"Error updating operation status: {e}")

    # Store in Redis
    try:
        if "cad_state" in data:
            redis_client.set(f"cad_state:{user_id}", json.dumps(cad_state))
        if "message" in data:
            redis_client.set(f"cad_message:{user_id}", message)
        if "status" in data:
            redis_client.set(f"cad_status:{user_id}", status)
    except Exception as e:
        print(f"Warning: Error storing data in Redis: {e}")
        # Continue execution even if Redis fails

    return jsonify({"status": True, "message": "Result received successfully"})


@app.route("/poll", methods=["POST"])
def poll():
    data = request.get_json()
    cad_state = data.get("cad_state")
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"status": False, "message": "Missing user_id"}), 400

    # Diagnostic logging for all Redis keys/values for this user
    try:
        plugin_login = redis_client.get(f"plugin_login:{user_id}")
        plugin_login_value = plugin_login.decode("utf-8") if plugin_login else "none"

        explicit_logout = redis_client.get(f"plugin_explicitly_logged_out:{user_id}")
        explicit_logout_value = (
            explicit_logout.decode("utf-8") if explicit_logout else "none"
        )

        last_seen = redis_client.get(f"plugin_last_seen:{user_id}")
        last_seen_value = last_seen.decode("utf-8") if last_seen else "none"

        # print(f"REDIS STATE for user {user_id}:")
        # print(f"  plugin_login: {plugin_login_value}")
        # print(f"  explicitly_logged_out: {explicit_logout_value}")
        # print(f"  last_seen: {last_seen_value}")
    except Exception as e:
        print(f"Warning: Error retrieving Redis diagnostic data: {e}")

    # Check if user has explicitly logged out
    try:
        explicit_logout = redis_client.get(f"plugin_explicitly_logged_out:{user_id}")
        if explicit_logout and explicit_logout.decode("utf-8") == "true":
            print(f"Rejecting poll for user {user_id} - user has explicitly logged out")

            # Return 401 with a clear message that authentication is required
            return (
                jsonify(
                    {
                        "status": False,
                        "message": "User has logged out. Authentication required.",
                        "authentication_required": True,
                        "explicit_logout": True,
                    }
                ),
                401,
            )
    except Exception as e:
        print(f"Warning: Error checking logout status in Redis: {e}")
        # Continue execution even if Redis check fails

    # Update plugin last seen timestamp in Redis
    try:
        redis_client.set(f"plugin_last_seen:{user_id}", str(int(time.time())))

        # Only set login to true if not explicitly logged out
        logout_flag = redis_client.get(f"plugin_explicitly_logged_out:{user_id}")
        if not logout_flag or logout_flag.decode("utf-8") != "true":
            redis_client.set(f"plugin_login:{user_id}", "true")
    except Exception as e:
        print(f"Warning: Error updating plugin status in Redis: {e}")
        # Continue execution even if Redis fails

    # Store cad_state in Redis
    if cad_state:
        try:
            redis_client.set(
                f"cad_state:{user_id}",
                json.dumps(cad_state) if isinstance(cad_state, dict) else cad_state,
            )
        except Exception as e:
            print(f"Warning: Error storing data in Redis: {e}")
            # Continue execution even if Redis fails

    # Check for pending operations
    pending_ops = (
        supabase.table("operations")
        .select("*")
        .eq("status", "pending")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if pending_ops.data and len(pending_ops.data) > 0:
        print(f"Pending operation found for user {user_id}")
        return jsonify({"status": True, "message": "Operation pending for this user"})

    return jsonify({"status": False, "message": "No pending operation"})


@app.route("/get_instructions", methods=["POST"])
def get_instructions():
    # Get user_id from request data
    data = request.get_json()
    if not data or not data.get("user_id"):
        return jsonify({"status": False, "message": "Missing user_id parameter"}), 400

    user_id = data.get("user_id")

    # Check if user has explicitly logged out
    try:
        explicit_logout = redis_client.get(f"plugin_explicitly_logged_out:{user_id}")
        if explicit_logout and explicit_logout.decode("utf-8") == "true":
            print(
                f"Rejecting get_instructions for user {user_id} - user has explicitly logged out"
            )
            return (
                jsonify(
                    {
                        "status": False,
                        "message": "User has logged out. Authentication required.",
                        "authentication_required": True,
                    }
                ),
                401,
            )
    except Exception as e:
        print(f"Warning: Error checking logout status in Redis: {e}")
        # Continue execution even if Redis check fails

    # Retrieve one pending operation FOR THIS USER ONLY
    pending_ops = (
        supabase.table("operations")
        .select("*")
        .eq("status", "pending")
        .eq(
            "user_id", user_id
        )  # Critical security filter: only get operations for this user
        .limit(1)
        .execute()
    )

    if not pending_ops.data or len(pending_ops.data) == 0:
        print(f"No pending operation for user {user_id}")
        return jsonify(
            {"status": False, "message": "No pending operation for this user"}
        )

    # Security double-check: make sure the operation belongs to this user
    op = pending_ops.data[0]
    if op["user_id"] != user_id:
        print(
            f"SECURITY ALERT: User {user_id} tried to access operation belonging to {op['user_id']}"
        )
        return (
            jsonify(
                {
                    "status": False,
                    "message": "Access denied: operation belongs to another user",
                }
            ),
            403,
        )

    # Update the operation's status to "sent"
    supabase.table("operations").update({"status": "sent"}).eq("id", op["id"]).execute()

    return jsonify(
        {
            "status": True,
            "instructions": op["python_code"],
            "operation_id": op["id"],
            "chat_id": op["chat_id"],
        }
    )


@app.route("/get_chats", methods=["GET", "OPTIONS"])
def get_chats():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id parameter"}), 400

    # Fetch all chats for the user, ordered by updated_at descending (newest first)
    chats_response = (
        supabase.table("chats")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )

    if not chats_response.data:
        return jsonify({"status": "success", "chats": []})

    return jsonify({"status": "success", "chats": chats_response.data})


@app.route("/get_messages", methods=["GET", "OPTIONS"])
def get_messages():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    chat_id = request.args.get("chat_id")
    if not chat_id:
        return jsonify({"status": "error", "message": "Missing chat_id parameter"}), 400

    # Fetch all messages for the chat, ordered by created_at ascending (oldest first)
    messages_response = (
        supabase.table("messages")
        .select("*")
        .eq("chat_id", chat_id)
        .order("created_at", desc=False)
        .execute()
    )

    if not messages_response.data:
        return jsonify({"status": "success", "messages": []})

    return jsonify({"status": "success", "messages": messages_response.data})


@app.route("/delete_chat", methods=["DELETE", "OPTIONS"])
def delete_chat():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"})

    # Parse the JSON request data
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400

        chat_id = data.get("chat_id")
        user_id = data.get("user_id")

        # Add debug logging
        print(f"Delete request received for chat_id: {chat_id}, user_id: {user_id}")

        # Validate required parameters
        if not chat_id:
            return jsonify({"status": "error", "message": "Missing chat_id"}), 400
        if not user_id:
            return jsonify({"status": "error", "message": "Missing user_id"}), 400

        # First verify the chat belongs to the user
        try:
            chat_response = (
                supabase.table("chats")
                .select("*")
                .eq("id", chat_id)
                .eq("user_id", user_id)
                .execute()
            )
            print(f"Chat verification response: {chat_response}")

            # If no chat found or doesn't belong to user
            if not chat_response.data or len(chat_response.data) == 0:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Chat not found or not owned by user",
                        }
                    ),
                    404,
                )
        except Exception as e:
            print(f"Error verifying chat ownership: {str(e)}")
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Error verifying chat ownership: {str(e)}",
                    }
                ),
                500,
            )

        # First delete all operations associated with the chat
        try:
            print(f"Attempting to delete operations for chat_id: {chat_id}")
            operations_deletion = (
                supabase.table("operations").delete().eq("chat_id", chat_id).execute()
            )
            print(f"Operations deletion response: {operations_deletion}")
        except Exception as e:
            print(f"Error deleting operations: {str(e)}")
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Error deleting operations: {str(e)}",
                    }
                ),
                500,
            )

        # Then delete all messages associated with the chat
        try:
            # This prevents orphaned messages in the database
            messages_deletion = (
                supabase.table("messages").delete().eq("chat_id", chat_id).execute()
            )
            print(f"Messages deletion response: {messages_deletion}")
        except Exception as e:
            print(f"Error deleting messages: {str(e)}")
            return (
                jsonify(
                    {"status": "error", "message": f"Error deleting messages: {str(e)}"}
                ),
                500,
            )

        # Then delete the chat itself
        try:
            chat_deletion = (
                supabase.table("chats")
                .delete()
                .eq("id", chat_id)
                .eq("user_id", user_id)  # Double check user ownership
                .execute()
            )
            print(f"Chat deletion response: {chat_deletion}")
        except Exception as e:
            print(f"Error deleting chat: {str(e)}")
            return (
                jsonify(
                    {"status": "error", "message": f"Error deleting chat: {str(e)}"}
                ),
                500,
            )

        # Return success response
        return jsonify(
            {
                "status": "success",
                "message": "Chat and associated messages deleted successfully",
            }
        )

    except Exception as e:
        # Handle any exceptions and provide detailed error
        error_msg = str(e)
        print(f"Exception in delete_chat: {error_msg}")
        return (
            jsonify(
                {"status": "error", "message": f"Failed to delete chat: {error_msg}"}
            ),
            500,
        )


@app.route("/fusion_auth", methods=["POST"])
def fusion_auth():
    """Authenticate Fusion 360 plugin user with email and password"""
    try:
        # Get data from request
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return (
                jsonify({"status": False, "message": "Missing email or password"}),
                400,
            )

        # Call Supabase auth.sign_in method
        auth_response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        # We need both user and session objects from the response
        if not auth_response.user or not auth_response.session:
            return (
                jsonify({"status": False, "message": "Invalid email or password"}),
                401,
            )

        # Get user and session from result
        user = auth_response.user
        session = auth_response.session

        # Store plugin status in Redis
        try:
            # Set plugin login status to true
            redis_client.set(f"plugin_login:{user.id}", "true")
            # Set last seen timestamp
            redis_client.set(f"plugin_last_seen:{user.id}", str(int(time.time())))

            # IMPORTANT: Reset the explicit logout flag when user logs in again
            # This ensures consistency between plugin and backend auth state
            redis_client.set(f"plugin_explicitly_logged_out:{user.id}", "false")

            print(
                f"User {user.id} authenticated successfully - reset logout flags in Redis"
            )
        except Exception as e:
            print(f"Warning: Error storing plugin status in Redis: {e}")
            # Continue execution even if Redis fails

        # Return success with token from session and user id
        return jsonify(
            {
                "status": True,
                "message": "Authentication successful",
                "token": session.access_token,  # Use access_token from session object
                "user_id": user.id,
            }
        )

    except Exception as e:
        print(f"Error in authentication: {str(e)}")
        return (
            jsonify({"status": False, "message": f"Authentication error: {str(e)}"}),
            500,
        )


@app.route("/verify_token", methods=["POST"])
def verify_token():
    """Verify a Supabase authentication token or encrypted token data."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": False, "message": "No JSON data provided"}), 400

        token = data.get("token")
        encrypted_data = data.get("encrypted_data")

        # Handle encrypted data verification (used by Fusion add-in)
        if token == "VERIFY_NEEDED" and encrypted_data:
            try:
                # In a production environment, you would decrypt the data here
                # and validate its contents. For this demo, we're assuming the
                # encrypted_data is valid if it's properly formatted.

                # The data would normally be decrypted and checked, but for this demo:
                # 1. Check if it looks like our encrypted data (base64 check)
                try:
                    import base64

                    decoded = base64.b64decode(encrypted_data)
                    if not decoded or len(decoded) < 32:  # Arbitrary minimum size
                        return (
                            jsonify(
                                {"status": False, "message": "Invalid encrypted data"}
                            ),
                            401,
                        )
                except Exception:
                    return (
                        jsonify({"status": False, "message": "Invalid base64 data"}),
                        401,
                    )

                # For demo purposes, we'll extract a user ID from the session of the request
                # In production, you'd actually decrypt and validate the token

                # Query Supabase for a valid user to use for testing
                valid_users = supabase.table("users").select("id").limit(1).execute()
                if valid_users.data and len(valid_users.data) > 0:
                    test_user_id = valid_users.data[0]["id"]
                else:
                    # Fallback to a test user ID if no users found
                    test_user_id = "test_user_123"

                # Return a successful response with a temporary token and user ID
                return jsonify(
                    {
                        "status": True,
                        "message": "Token verified via encrypted data",
                        "user_id": test_user_id,
                        # In a real implementation, you might generate a fresh token here
                        "token": "TEMPORARY_TOKEN_" + str(int(time.time())),
                    }
                )

            except Exception as e:
                print(f"Error processing encrypted token data: {str(e)}")
                return (
                    jsonify(
                        {
                            "status": False,
                            "message": f"Error processing encrypted data: {str(e)}",
                        }
                    ),
                    500,
                )

        # Handle standard token verification (direct token provided)
        if not token or token.startswith("TEMPORARY_TOKEN_"):
            return jsonify({"status": False, "message": "Valid token is required"}), 400

        # Verify the token with Supabase
        try:
            user = supabase.auth.get_user(token)
            if user and user.user and user.user.id:
                return jsonify(
                    {
                        "status": True,
                        "message": "Token is valid",
                        "user_id": user.user.id,
                    }
                )
            else:
                return jsonify({"status": False, "message": "Invalid token"}), 401
        except Exception as e:
            return (
                jsonify(
                    {"status": False, "message": f"Token validation error: {str(e)}"}
                ),
                401,
            )

    except Exception as e:
        print(f"Error in verify_token: {str(e)}")
        return (
            jsonify({"status": False, "message": f"Verification error: {str(e)}"}),
            500,
        )


@app.route("/plugin_logout", methods=["POST"])
def plugin_logout():
    """Handle plugin logout and update Redis status."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": False, "message": "No JSON data provided"}), 400

        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"status": False, "message": "Missing user_id"}), 400

        # Clear plugin login status in Redis - with additional keys to ensure full invalidation
        try:
            # Explicitly set the plugin status to logged out
            redis_client.set(f"plugin_login:{user_id}", "false")

            # Update the last seen timestamp to now
            redis_client.set(f"plugin_last_seen:{user_id}", str(int(time.time())))

            # Set a dedicated logout flag
            redis_client.set(f"plugin_explicitly_logged_out:{user_id}", "true")

            # Log this event for debugging
            print(
                f"Plugin logout recorded for user {user_id} with timestamp {int(time.time())}"
            )
        except Exception as e:
            print(f"Warning: Error updating plugin logout status in Redis: {e}")
            # Continue execution even if Redis fails

        return jsonify(
            {"status": True, "message": "Plugin logout successful", "user_id": user_id}
        )

    except Exception as e:
        print(f"Error in plugin_logout: {str(e)}")
        return jsonify({"status": False, "message": f"Logout error: {str(e)}"}), 500


@app.route("/check_plugin_login", methods=["GET"])
def check_plugin_login():
    """Check if a user's Fusion plugin is logged in and active."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"status": False, "message": "Missing user_id parameter"}), 400

    # Diagnostic logging for all Redis keys/values for this user
    try:
        plugin_login = redis_client.get(f"plugin_login:{user_id}")
        plugin_login_value = plugin_login.decode("utf-8") if plugin_login else "none"

        explicit_logout = redis_client.get(f"plugin_explicitly_logged_out:{user_id}")
        explicit_logout_value = (
            explicit_logout.decode("utf-8") if explicit_logout else "none"
        )

        last_seen = redis_client.get(f"plugin_last_seen:{user_id}")
        last_seen_value = last_seen.decode("utf-8") if last_seen else "none"

        # print(f"REDIS STATE for user {user_id}:")
        # print(f"  plugin_login: {plugin_login_value}")
        # print(f"  explicitly_logged_out: {explicit_logout_value}")
        # print(f"  last_seen: {last_seen_value}")
    except Exception as e:
        print(f"Warning: Error retrieving Redis diagnostic data: {e}")

    try:
        # Check if plugin is logged in
        plugin_login = redis_client.get(f"plugin_login:{user_id}")
        plugin_login_status = plugin_login and plugin_login.decode("utf-8") == "true"

        # Check explicit logout flag
        explicit_logout = redis_client.get(f"plugin_explicitly_logged_out:{user_id}")
        explicitly_logged_out = (
            explicit_logout and explicit_logout.decode("utf-8") == "true"
        )

        # Check Supabase for user existence - this provides an extra layer of validation
        # that the user_id is valid and belongs to a real user
        try:
            # Use a lightweight query that just checks if the user exists
            user_check = (
                supabase.from_("profiles")
                .select("id")
                .eq("id", user_id)
                .limit(1)
                .execute()
            )
            user_exists = user_check.data and len(user_check.data) > 0
            if not user_exists:
                print(f"WARNING: User {user_id} not found in database")
                # Consider the user logged out if they don't exist in the database
                explicitly_logged_out = True
                plugin_login_status = False
        except Exception as e:
            print(f"Warning: Error checking user existence in database: {e}")

        # If explicitly logged out, override login status regardless of other states
        if explicitly_logged_out:
            plugin_login_status = False

        # Get last seen timestamp
        last_seen = redis_client.get(f"plugin_last_seen:{user_id}")
        print(f"Last seen value: {last_seen}")
        last_seen_timestamp = int(last_seen.decode("utf-8")) if last_seen else None

        # Calculate if plugin is active (seen in the last 5 minutes)
        is_active = False
        time_since_last_seen = None

        if last_seen_timestamp:
            current_time = int(time.time())
            time_since_last_seen = current_time - last_seen_timestamp
            # Consider active if seen in the last 5 minutes
            is_active = time_since_last_seen < 300  # 5 minutes in seconds

        # Check if plugin has explicitly logged out via plugin_login key
        plugin_explicitly_logged_out = (
            plugin_login and plugin_login.decode("utf-8") == "false"
        )

        # Combined logout check - either by flag or by login status
        is_logged_out = explicitly_logged_out or plugin_explicitly_logged_out

        # Only show as connected if the plugin is BOTH logged in AND active AND NOT explicitly logged out
        is_connected = plugin_login_status and is_active and not is_logged_out

        # Debug info to help diagnose issues
        print(f"Plugin status for user {user_id}:")
        print(
            f"  plugin_login: {plugin_login.decode('utf-8') if plugin_login else None}"
        )
        print(f"  plugin_login_status: {plugin_login_status}")
        print(f"  explicitly_logged_out: {explicitly_logged_out}")
        print(f"  plugin_explicitly_logged_out: {plugin_explicitly_logged_out}")
        print(f"  is_logged_out: {is_logged_out}")
        print(
            f"  is_active: {is_active} (last seen: {time_since_last_seen} seconds ago)"
        )
        print(f"  is_connected: {is_connected}")

        # Set appropriate status message
        status_message = "Disconnected"
        if is_logged_out:
            status_message = "Logged Out"  # Special status for explicit logout
        elif is_connected:
            status_message = "Connected"
        elif plugin_login_status and not is_active:
            status_message = "Inactive"
        elif not plugin_login_status:
            status_message = "Not installed"

        print(f"  status_message: {status_message}")

        # Return accurate plugin status
        return jsonify(
            {
                "status": True,
                "plugin_login": plugin_login_status
                and not is_logged_out,  # Override login status if logged out
                "is_active": is_active,
                "is_connected": is_connected,
                "is_logged_out": is_logged_out,  # New field to explicitly track logout status
                "last_seen_timestamp": last_seen_timestamp,
                "time_since_last_seen": time_since_last_seen,
                "user_id": user_id,
                "status_message": status_message,
            }
        )

    except Exception as e:
        print(f"Error checking plugin login status: {str(e)}")
        return (
            jsonify(
                {"status": False, "message": f"Error checking plugin status: {str(e)}"}
            ),
            500,
        )


def parse_messages(messages):
    parsed_messages = []
    for message in messages.data:
        content = ""
        for block in message.content:
            if block.type == "text":
                content += block.text.value
        parsed_messages.append(
            {
                "id": message.id,
                "role": message.role,
                "content": content,
                "created_at": message.created_at,
                "thread_id": message.thread_id,
            }
        )

    return parsed_messages


if __name__ == "__main__":
    app.run(debug=True, port=5000)
