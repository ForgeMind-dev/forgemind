// src/renderer/components/ChatWindow.tsx

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Chat } from '../types';

interface ChatWindowProps {
  chats: Chat[];
  activeChatIndex: number;
  fullLogo: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  chats,
  activeChatIndex,
  fullLogo,
}) => {
  const currentChat = chats[activeChatIndex];

  if (currentChat.messages.length === 0) {
    return (
      <div className="center-content">
        <img src={fullLogo} alt="ForgeMind Logo" className="main-logo" />
        <h1>What do you want to design today?</h1>
      </div>
    );
  }

  return (
    <div className="messages-container">
      {currentChat.messages.map((msg, idx) =>
        msg.role === "user" ? (
          <div key={idx} className="msg user-msg">
            {msg.content}
          </div>
        ) : (
          <div key={idx} className="msg ai-msg">
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        )
      )}
    </div>
  );
};

export default ChatWindow;
