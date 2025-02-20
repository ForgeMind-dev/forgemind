# forgemind-backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from pydantic import BaseModel, ValidationError
import openai

# Load environment variables from .env file
load_dotenv()

# Retrieve Supabase URL and Anon Key from environment variables
SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = Flask(__name__)
CORS(app)  # Enable CORS for communication with your Electron app

class PromptPayload(BaseModel):
    text: str
    user_id: str

@app.route('/chat', methods=['POST'])
def handle_prompt():
    try:
        data = PromptPayload(**request.get_json())
    except ValidationError as e:
        return jsonify({"status": "error", "message": "Invalid payload", "errors": e.errors()}), 400
    
    response = supabase.table("operations").insert({
        "text": data.text,
        "user_id": data.user_id,
    }).execute()

    openai.api_key = os.getenv("OPENAI_API_KEY")

    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": data.text},
        ]
    )

    assistant_message = chat_response["choices"][0]["message"]["content"]
    print("ChatGPT response:", assistant_message)
    
    # You can also add logic here to process the prompt using AI/NLP
    return jsonify({"status": "success", "operation": response.data})

@app.route('/test_db', methods=['GET'])
def test_db():
    # Query the "chats" table
    response = supabase.table("chats").select("*").execute()
    return jsonify({"status": "success", "data": response.data})

# Endpoint for acknowledging operation completion
@app.route('/ack', methods=['POST'])
def acknowledge_operation():
    data = request.get_json()
    operation_id = data.get("operation_id")
    
    # Update the operation record's status in Supabase to "completed"
    response = supabase.table("operations").update({"status": "completed"}).eq("id", operation_id).execute()
    return jsonify({"status": "acknowledged", "operation_id": operation_id})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
