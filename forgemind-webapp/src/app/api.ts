// forgemind-webapp/src/app/api.ts

// Use an environment variable for the backend URL
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

/**
 * Sends a user prompt to the backend via the /chat endpoint.
 * @param text The text prompt (e.g., "create a circle")
 * @param userId The user's ID (from Supabase Auth)
 * @param threadId (Optional) The thread ID to include in the request body.
 */
export async function sendPrompt(text: string, userId: string, threadId?: string) {
  const body: any = { text, user_id: userId };
  if (threadId) {
    body.thread_id = threadId;
  }
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`Error sending prompt: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Sends an acknowledgment for an operation to the backend via /ack.
 * @param operationId The ID of the operation to acknowledge.
 */
export async function acknowledgeOperation(operationId: string) {
  const response = await fetch(`${API_BASE_URL}/ack`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ operation_id: operationId })
  });

  if (!response.ok) {
    throw new Error(`Error acknowledging operation: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * (Optional) Poll for pending operations via /poll.
 */
export async function pollOperation() {
  const response = await fetch(`${API_BASE_URL}/poll`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`Error polling for operation: ${response.statusText}`);
  }
  
  return response.json();
}
