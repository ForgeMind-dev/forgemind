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

# Initialize Redis client
redis_client = Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)
# Explicitly allow all origins and support credentials
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


class ChatPayload(BaseModel):
    text: str
    user_id: str


@app.route("/chat", methods=["OPTIONS", "POST"])
def chat():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response

    try:
        data = ChatPayload(**request.get_json())
    except ValidationError as e:
        return (
            jsonify(
                {"status": "error", "message": "Invalid payload", "errors": e.errors()}
            ),
            400,
        )

    chat_insertion = (
        supabase.table("chats")
        .insert(
            {
                "text": data.text,
                "user_id": data.user_id,
                "assistant_id": "asst_oXIfV78tGu083fATRFRY7HMW",
            }
        )
        .execute()
    )

    thread = client.beta.threads.create()

    # Add a message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=data.text
    )

    # Create a run
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id="asst_oXIfV78tGu083fATRFRY7HMW"
    )

    # Wait for the run to complete
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Get the messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Accumulate the assistant's response
    assistant_response = ""
    for message in messages.data:
        if message.role == "assistant":
            message_chunk = message.content[0].text.value
            assistant_response += message_chunk

    supabase.table("operations").insert(
        {
            "instructions": assistant_response,
            "chat_id": chat_insertion.data[0]["id"],
            "user_id": data.user_id,
            "cad_type": "fusion",
            "status": "pending",
        }
    ).execute()

    return jsonify({"status": "success", "response": assistant_response})


@app.route("/poll", methods=["POST"])
def poll():
    data = request.get_json()
    cad_state = data.get("cad_state")
    
    # Store cad_state in Redis
    if cad_state:
        redis_client.set(f"cad_state:{data['user_id']}", cad_state)
    
    # Retrieve one pending operation
    pending_ops = (
        supabase.table("operations")
        .select("*")
        .eq("status", "pending")
        .limit(1)
        .execute()
    )
    if not pending_ops.data:
        return jsonify({"status": False, "message": "No pending operation found"})

    return jsonify({"status": True, "message": "Operation pending"})


@app.route("/get_instructions", methods=["POST"])
def get_instructions():
    # Retrieve one pending operation
    pending_ops = (
        supabase.table("operations")
        .select("*")
        .eq("status", "pending")
        .limit(1)
        .execute()
    )
    if not pending_ops.data:
        return jsonify({"status": False, "message": "No pending operation found"})

    operation = pending_ops.data[0]

    # Update its status to "sent"
    supabase.table("operations").update({"status": "sent"}).eq(
        "id", operation["id"]
    ).execute()

    # Return the instructions from the operation
    instructions = operation["instructions"]
    pattern = r"```(?:python)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, instructions)
    cleaned_instructions = match.group(1) if match else instructions.strip()
    return jsonify({"status": True, "instructions": cleaned_instructions})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
