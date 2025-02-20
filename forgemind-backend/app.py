# forgemind-backend/app.py

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

    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
)

    assistant_message = chat_completion.choices[0].message.content
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
