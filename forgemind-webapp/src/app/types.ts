// src/renderer/types.ts

export interface Message {
  role: "user" | "assistant" | "system";
  content: { user_facing_response: string };
}

export interface Chat {
  id?: string;  // Our database primary key (UUID) - used for URL navigation
  name: string;
  messages: Message[];
  visible?: boolean; // if false, hide this chat in the UI
  threadId?: string; // OpenAI's thread ID - used for continuing conversations with the API
  error?: boolean; // if true, there was an error loading this chat's messages
  updated_at?: string; // ISO string timestamp of when the chat was last updated
}

