import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Chat } from '../types';
import { useLocation } from 'react-router-dom';
import '../styles/ChatWindow.css';
import { containsPythonCADCode } from '../utils/messageUtils';

interface ChatWindowProps {
  chats: Chat[];
  activeChatIndex: number;
  fullLogo: string;
  isLoading: boolean;
  isNavigating?: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  chats,
  activeChatIndex,
  isLoading,
  isNavigating = false,
}) => {
  // All hooks must be called at the top level, unconditionally
  const [loadingText, setLoadingText] = useState("Designing");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const location = useLocation();
  
  // Check if we're in new chat mode or if the selected chat doesn't exist
  const isEmptyState = activeChatIndex === -1 || !chats[activeChatIndex];
  
  // Safely get the current chat
  const currentChat = !isEmptyState ? chats[activeChatIndex] : null;
  
  // Safely determine the base text for loading
  const lastUserMessage = currentChat?.messages
    ?.slice()
    ?.reverse()
    ?.find((msg) => msg.role === "user")?.content || "";
    
  const baseText = lastUserMessage.trim().split(' ')[0].toLowerCase() === "design"
    ? "Designing"
    : "Reasoning";

  // Render a single message with fade-in animation
  const renderMessage = (message: any, index: number) => {
    const isUser = message.role === 'user';
    
    // Filter Python code in assistant messages
    let content = message.content;
    if (!isUser && containsPythonCADCode(content)) {
      content = "Design created! Let me know if you need any modifications or want to start a new design.";
    }
    
    return (
      <div 
        key={index} 
        className={`msg ${isUser ? 'user-msg' : 'ai-msg'}`}
      >
        <div className="markdown-content">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    );
  };

  // Auto-scroll effect - runs conditionally based on dependencies, but the hook itself is unconditional
  useEffect(() => {
    if (messagesEndRef.current && currentChat) {
      // Scroll to the bottom
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [currentChat?.messages, isLoading]);

  // Animate the loading text - also unconditional hook call
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      let dots = 0;
      interval = setInterval(() => {
        setLoadingText(`${baseText}${'.'.repeat(dots)}`);
        dots = (dots + 1) % 4;
      }, 500);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isLoading, baseText]);

  // If we're in the empty state, show the prompt
  if (isEmptyState) {
    return (
      <div className="center-content">
        <h1>What can I help with?</h1>
      </div>
    );
  }

  // Otherwise, render the messages
  return (
    <div ref={messagesEndRef} className="messages-container">
      {currentChat?.messages.map((message, index) => 
        renderMessage(message, index)
      )}
      
      {/* Show only a single loading indicator - no need for multiple states */}
      {(isLoading || isNavigating) && (
        <div className="msg ai-msg loading-bubble">
          <div className="loading-indicator" style={{ display: 'flex', alignItems: 'center' }}>
            <div className="spinner" style={{ marginRight: '8px' }}></div>
            <span>Reasoning...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
