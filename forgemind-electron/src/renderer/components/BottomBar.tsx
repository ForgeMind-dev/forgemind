// src/renderer/components/BottomBar.tsx
import React, { KeyboardEvent } from 'react';

interface BottomBarProps {
  input: string;
  setInput: (value: string) => void;
  onSend: () => void;
  logoIcon: string;
}

const BottomBar: React.FC<BottomBarProps> = ({
  input,
  setInput,
  onSend,
  logoIcon,
}) => {
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") onSend();
  };

  return (
    <div className="bottom-bar">
      <div className="chat-bubble">
        <div className="chat-bubble-icon">
          <img src={logoIcon} alt="Chat Icon" className="chat-icon-img" />
        </div>
        <input
          className="chat-bubble-input"
          placeholder="Start building with ForgeMind..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="chat-bubble-send-btn" onClick={onSend}>
          &#9658;
        </button>
      </div>
    </div>
  );
};

export default BottomBar;
