import React, { useState, useEffect, useRef } from 'react';
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
  isLoading,
}) => {
  const currentChat = chats[activeChatIndex];
  const [loadingText, setLoadingText] = useState("Designing");

  // 1. Ref for the messages container
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 2. Auto-scroll effect
  useEffect(() => {
    if (messagesEndRef.current) {
      // Scroll to the bottom
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [currentChat.messages, isLoading]);

  // Determine the base text (Designing vs. Reasoning)
  const lastUserMessage =
    currentChat.messages.slice().reverse().find((msg) => msg.role === "user")?.content || "";
  const baseText =
    lastUserMessage.trim().split(' ')[0].toLowerCase() === "design"
      ? "Designing"
      : "Reasoning";

  // Animate the "Designing..." or "Reasoning..." text
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      let dots = 0;
      interval = setInterval(() => {
        dots = (dots + 1) % 4;
        setLoadingText(baseText + ".".repeat(dots));
      }, 500);
    } else {
      setLoadingText(baseText);
    }
    return () => clearInterval(interval);
  }, [isLoading, baseText]);

  // If there are no messages, show the empty state
  if (!currentChat.messages.length) {
    return (
      <div className="center-content">
        <h1>What can I help with?</h1>
      </div>
    );
  }

  // Otherwise show the messages
  return (
    <div ref={messagesEndRef} className="messages-container">
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
