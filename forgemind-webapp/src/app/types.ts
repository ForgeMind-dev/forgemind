// src/renderer/types.ts

export interface Message {
    role: "user" | "assistant";
    content: string;
  }
  
  export interface Chat {
    name: string;
    messages: Message[];
    visible?: boolean; // if false, hide this chat in the UI
    threadId?: string;
  }
  
  