# forgemind-backend/app.py

import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from pydantic import BaseModel, ValidationError
from openai import OpenAI

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
CORS(app)  # Enable CORS for communication with your Electron app

class ChatPayload(BaseModel):
    text: str
    user_id: str

class AuthPayload(BaseModel):
    email: str
    password: str

@app.route('/auth/verify', methods=['POST'])
def verify_credentials():
    try:
        data = AuthPayload(**request.get_json())
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": "Invalid payload",
            "errors": e.errors(),
            "is_valid": False
        }), 400
    
    try:
        # Attempt to sign in with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        # If we get here, authentication was successful
        return jsonify({
            "status": "success",
            "message": "Authentication successful",
            "is_valid": True,
            "session": {
                "access_token": response.session.access_token if response.session else None,
                "user": {
                    "email": response.user.email if response.user else None,
                    "id": response.user.id if response.user else None
                } if response.user else None
            }
        })
    except Exception as e:
        # Handle specific Supabase error types
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password",
                "is_valid": False
            }), 401
        elif "rate limit" in error_msg.lower():
            return jsonify({
                "status": "error",
                "message": "Too many login attempts. Please try again later",
                "is_valid": False
            }), 429
        else:
            return jsonify({
                "status": "error",
                "message": "Authentication failed",
                "is_valid": False
            }), 500

@app.route('/auth/validate-session', methods=['POST'])
def validate_session():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            "status": "error",
            "message": "No token provided",
            "is_valid": False
        }), 401
    
    token = auth_header.split(' ')[1]
    try:
        # Verify the token with Supabase
        user = supabase.auth.get_user(token)
        return jsonify({
            "status": "success",
            "message": "Session is valid",
            "is_valid": True,
            "user": {
                "email": user.user.email,
                "id": user.user.id
            } if user and user.user else None
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Invalid or expired session",
            "is_valid": False
        }), 401

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = ChatPayload(**request.get_json())
    except ValidationError as e:
        return jsonify({"status": "error", "message": "Invalid payload", "errors": e.errors()}), 400
    
    response = supabase.table("chats").insert({
        "text": data.text,
        "user_id": data.user_id,
    }).execute()

    thread = client.beta.threads.create()

    # Add a message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=data.text
    )

    # Create a run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id='asst_oXIfV78tGu083fATRFRY7HMW'
    )

    # Wait for the run to complete
    while run.status != "completed":
        print('running...')
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Get the messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Print the assistant's response
    response = ''
    for message in messages.data:
        if message.role == "assistant":
            message_chunk = message.content[0].text.value
            print(message_chunk, end='')
            response += message_chunk
    
    # You can also add logic here to process the prompt using AI/NLP
    return jsonify({"status": "success", "response": response})

@app.route('/poll', methods=['GET'])
def poll():
    return "app = adsk.core.Application.get()\nui = app.userInterface\nui.messageBox('Hi')"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
