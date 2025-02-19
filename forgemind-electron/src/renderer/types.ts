// src/renderer/types.ts

export interface Message {
    role: "user" | "assistant";
    content: string;
  }
  
  export interface Chat {
    name: string;
    messages: Message[];
  }
  