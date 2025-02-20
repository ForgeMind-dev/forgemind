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
    # return "app = adsk.core.Application.get()\nui = app.userInterface\n\ndesign = app.activeProduct\nrootComp = design.rootComponent\nsketches = rootComp.sketches\nxyPlane = rootComp.xYConstructionPlane\nsketch = sketches.add(xyPlane)\n\ncircles = sketch.sketchCurves.sketchCircles\nlines = sketch.sketchCurves.sketchLines\n\n# Draw a star using lines\ncenterPoint = adsk.core.Point3D.create(0, 0, 0)\npoints = []\nnum_points = 5\nouter_radius = 4\ninner_radius = 2\n\nfor i in range(num_points * 2):\n    angle = math.pi / num_points * i  # Twice the number of points for the star\n    if i % 2 == 0:\n        radius = outer_radius\n    else:\n        radius = inner_radius\n    x = radius * math.cos(angle)\n    y = radius * math.sin(angle)\n    points.append(adsk.core.Point3D.create(x, y, 0))\n\nfor i in range(len(points)):\n    line = lines.addByTwoPoints(points[i], points[(i + 2) % len(points)])"
    return "app = adsk.core.Application.get()\nui = app.userInterface\nui.messageBox('Hi')"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
