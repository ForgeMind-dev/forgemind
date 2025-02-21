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

app = Flask(__name__)
# Explicitly allow all origins and support credentials
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


class GetThreadsPayload(BaseModel):
    user_id: str


class CreateThreadPayload(BaseModel):
    user_id: str


class GetChatsPayload(BaseModel):
    user_id: str
    thread_id: str


class ChatPayload(BaseModel):
    text: str
    user_id: str
    thread_id: str


@app.route("/create_thread", methods=["OPTIONS", "POST"])
def create_thread():
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
        data = CreateThreadPayload(**request.get_json())
    except ValidationError as e:
        return (
            jsonify(
                {"status": "error", "message": "Invalid payload", "errors": e.errors()}
            ),
            400,
        )

    thread = client.beta.threads.create()
    thread_insertion = (
        supabase.table("assistant_threads")
        .insert(
            {
                "user_id": data.user_id,
                "assistant_id": "asst_oXIfV78tGu083fATRFRY7HMW",
                "thread_id": thread.id,
            }
        )
        .execute()
    )

    return jsonify({"thread_id": thread.id})


@app.route("/get_threads", methods=["OPTIONS", "POST"])
def get_threads():
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
        data = GetThreadsPayload(**request.get_json())
    except ValidationError as e:
        return (
            jsonify(
                {"status": "error", "message": "Invalid payload", "errors": e.errors()}
            ),
            400,
        )

    threads = (
        supabase.table("assistant_threads")
        .select("*")
        .eq("user_id", data.user_id)
        .execute()
    )
    return jsonify(threads.data)


@app.route("/get_chats", methods=["OPTIONS", "POST"])
def get_chats():
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
        data = GetChatsPayload(**request.get_json())
    except ValidationError as e:
        return (
            jsonify(
                {"status": "error", "message": "Invalid payload", "errors": e.errors()}
            ),
            400,
        )

    chats = (
        supabase.table("chats")
        .select("*")
        .eq("user_id", data.user_id)
        .eq("thread_id", data.thread_id)
        .execute()
    )
    return jsonify(chats.data)


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
                "thread_id": data.thread_id,
            }
        )
        .execute()
    )

    # Add a message to the thread
    message = client.beta.threads.messages.create(
        thread_id=data.thread_id, role="user", content=data.text
    )

    # Create a run
    run = client.beta.threads.runs.create(
        thread_id=data.thread_id, assistant_id="asst_oXIfV78tGu083fATRFRY7HMW"
    )

    # Wait for the run to complete
    while run.status != "completed":
        print("running...")
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=data.thread_id, run_id=run.id)

    # Get the messages from the thread
    messages = client.beta.threads.messages.list(thread_id=data.thread_id)

    # Accumulate the assistant's response
    assistant_response = ""
    for message in messages.data:
        if message.role == "assistant":
            message_chunk = message.content[0].text.value
            print(message_chunk, end="")
            assistant_response += message_chunk

    insert_operation = (
        supabase.table("operations")
        .insert(
            {
                "instructions": assistant_response,
                "chat_id": chat_insertion.data[0]["id"],
                "user_id": data.user_id,
                "cad_type": "fusion",
                "status": "pending",
            }
        )
        .execute()
    )

    return jsonify({"status": "success", "response": assistant_response})


@app.route("/poll", methods=["GET"])
def poll():
    print("polling...")
    # Retrieve one pending operation
    pending_ops = (
        supabase.table("operations")
        .select("*")
        .eq("status", "pending")
        .limit(1)
        .execute()
    )
    if not pending_ops.data:
        return (
            jsonify({"status": "error", "message": "No pending operation found"}),
            404,
        )

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
    return jsonify({"status": "success", "instructions": cleaned_instructions})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
