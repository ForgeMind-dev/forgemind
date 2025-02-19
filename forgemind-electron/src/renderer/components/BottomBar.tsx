// src/renderer/components/BottomBar.tsx

import React, { KeyboardEvent } from 'react';

interface BottomBarProps {
  input: string;
  setInput: (value: string) => void;
  onSend: () => void;
  logoIcon: string;
  onOptimize: () => void;
  onRefine: () => void;
  onRelations: () => void;
}

const BottomBar: React.FC<BottomBarProps> = ({
  input,
  setInput,
  onSend,
  logoIcon,
  onOptimize,
  onRefine,
  onRelations,
}) => {
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") onSend();
  };

  return (
    <div className="bottom-bar">
      <div className="quick-actions">
        <button className="quick-pill">Suggest a CAD Tool</button>
        <button className="quick-pill" onClick={onOptimize}>
          Optimize Tolerances
        </button>
        <button className="quick-pill" onClick={onRefine}>
          Refine Curved Surfaces
        </button>
        <button className="quick-pill">Run Crash Analysis</button>
        <button className="quick-pill" onClick={onRelations}>
          View Part Relations
        </button>
      </div>
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
