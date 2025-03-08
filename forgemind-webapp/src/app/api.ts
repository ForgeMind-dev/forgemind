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
  // threadId is OpenAI's thread ID, which is stored in our database's thread_id column
  // The API will return both thread_id (OpenAI) and chat_id (our database primary key)
  const body: any = { text, user_id: userId };
  if (threadId) {
    body.thread_id = threadId;
  }
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    mode: 'cors',
    credentials: 'omit',
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`Error sending prompt: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Retrieves all chats for a user.
 * @param userId The user's ID (from Supabase Auth)
 */
export async function getUserChats(userId: string) {
  const response = await fetch(`${API_BASE_URL}/get_chats?user_id=${encodeURIComponent(userId)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
    mode: 'cors',
    credentials: 'omit'
  });

  if (!response.ok) {
    throw new Error(`Error retrieving chats: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Deletes a chat and all its messages from the database.
 * @param chatId The ID of the chat to delete
 * @param userId The user's ID who owns the chat
 */
export async function deleteChat(chatId: string, userId: string) {
  console.log(`Attempting to delete chat: ${chatId} for user: ${userId}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/delete_chat`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      mode: 'cors',
      credentials: 'omit',
      body: JSON.stringify({
        chat_id: chatId,
        user_id: userId
      })
    });

    console.log(`Delete response status: ${response.status}`);
    
    const data = await response.json();
    console.log('Delete response data:', data);
    
    if (!response.ok) {
      // If we got a response but with error status
      const errorMessage = data.message || response.statusText;
      throw new Error(`Error deleting chat: ${errorMessage}`);
    }
    
    return data;
  } catch (error) {
    console.error('Error in deleteChat:', error);
    throw error;
  }
}

/**
 * Retrieves messages for a specific chat.
 * @param chatId The ID of the chat
 */
export async function getChatMessages(chatId: string) {
  try {
    console.log(`Fetching messages for chat: ${chatId}`);
    const response = await fetch(`${API_BASE_URL}/get_messages?chat_id=${chatId}`, {
      mode: 'cors',
      credentials: 'omit'
    });
    
    // If we get a 500 error, log it but don't throw an error
    // Instead return an empty messages array
    if (response.status === 500) {
      console.warn(`Server error fetching messages for chat ${chatId}. The server might be experiencing issues.`);
      return { messages: [] };
    }
    
    if (!response.ok) {
      throw new Error(`Error retrieving messages: ${response.statusText}`);
    }
    
    return response.json();
  } catch (error) {
    console.error(`Error in getChatMessages for ${chatId}:`, error);
    // Return empty messages instead of throwing to prevent UI crashes
    return { messages: [] };
  }
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

/**
 * Checks if the user's Fusion plugin is logged in and active.
 * @param userId The user's ID
 * @returns Object with plugin login status information
 */
export async function checkPluginLoginStatus(userId: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/check_plugin_login?user_id=${encodeURIComponent(userId)}`, {
      mode: 'cors',
      credentials: 'omit'
    });
    
    if (!response.ok) {
      console.warn(`Error checking plugin login status: ${response.statusText}`);
      return { 
        status: false, 
        plugin_login: false, 
        is_active: false,
        is_connected: false,
        is_logged_out: false,
        error: response.statusText
      };
    }
    
    const result = await response.json();
    
    // Log status to help with debugging
    console.log(`Plugin status for ${userId}:`, {
      plugin_login: result.plugin_login,
      is_active: result.is_active,
      is_connected: result.is_connected,
      is_logged_out: result.is_logged_out,
      status_message: result.status_message
    });
    
    return result;
  } catch (error) {
    console.error('Error checking plugin login status:', error);
    return { 
      status: false, 
      plugin_login: false, 
      is_active: false,
      is_connected: false,
      is_logged_out: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}
