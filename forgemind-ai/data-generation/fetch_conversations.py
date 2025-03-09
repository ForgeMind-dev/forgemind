import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Supabase URL and Anon Key from environment variables
SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def fetch_conversations():
    # Fetch all chats
    chats_response = supabase.table("chats").select("*").order("created_at", desc=False).execute()
    chats = chats_response.data

    for chat in chats:
        chat_id = chat["id"]
        print(f"Chat ID: {chat_id}, Title: {chat['title']}")

        # Fetch messages for the chat
        messages_response = supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at", desc=False).execute()
        messages = messages_response.data
        for message in messages:
            print(f"  Message ID: {message['id']}, Content: {message['content']}")

        # Fetch operations for the chat
        operations_response = supabase.table("operations").select("*").eq("chat_id", chat_id).order("created_at", desc=False).execute()
        operations = operations_response.data
        for operation in operations:
            print(f"  Operation ID: {operation['id']}, Instructions: {operation['instructions']}")

if __name__ == "__main__":
    fetch_conversations()
