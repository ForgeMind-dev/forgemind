import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Chat } from '../types';

interface ChatWindowProps {
  chats: Chat[];
  activeChatIndex: number;
  fullLogo: string;
  isLoading: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  chats,
  activeChatIndex,
  fullLogo,
  isLoading,
}) => {
  const currentChat = chats[activeChatIndex];
  const [loadingText, setLoadingText] = useState("Designing");

  // Get the most recent user message (if any)
  const lastUserMessage =
    currentChat.messages.slice().reverse().find((msg) => msg.role === "user")?.content || "";
  // Determine the base text based on the first word of the last user message.
  const baseText =
    lastUserMessage.trim().split(' ')[0].toLowerCase() === "design"
      ? "Designing"
      : "Reasoning";

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      let dots = 0;
      interval = setInterval(() => {
        dots = (dots + 1) % 4;
        setLoadingText(baseText + ".".repeat(dots));
      }, 500);
    } else {
      setLoadingText(baseText); // Reset text when not loading
    }
    return () => {
      clearInterval(interval);
    };
  }, [isLoading, baseText]);

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
      {isLoading && (
        <div className="msg ai-msg loading-bubble">
          <div className="loading-indicator" style={{ display: 'flex', alignItems: 'center' }}>
            <div className="spinner" style={{ marginRight: '8px' }}></div>
            <span>{loadingText}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
