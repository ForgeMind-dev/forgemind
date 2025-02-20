# forgemind-backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Retrieve Supabase URL and Anon Key from environment variables
SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

app = Flask(__name__)
CORS(app)  # Enable CORS for communication with your Electron app

# Example endpoint to receive text prompts
@app.route('/prompt', methods=['POST'])
def handle_prompt():
    data = request.get_json()
    user_prompt = data.get("prompt")
    user_id = data.get("user_id")  # Use this to associate with a Supabase user
    
    # Example: Insert a new operation record into Supabase
    # In a real app, you might first create or update a chat record, then create an operation.
    operation_data = {
        "chat_id": None,  # Replace with an actual chat id or create a new chat record
        "operation_type": "create_circle",
        "parameters": {"radius": 10},
        "status": "pending"
    }
    response = supabase.table("operations").insert(operation_data).execute()
    
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
