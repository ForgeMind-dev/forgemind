import React, { KeyboardEvent, Dispatch, SetStateAction, useRef } from "react";

interface BottomBarProps {
  input: string;
  setInput: Dispatch<SetStateAction<string>>;
  onSend: () => void;
  logoIcon: string;
  className?: string;
}

const BottomBar: React.FC<BottomBarProps> = ({
  input,
  setInput,
  onSend,
  logoIcon,
  className = "",
}) => {
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const autoResize = () => {
    if (textAreaRef.current) {
      // Reset height to auto to shrink it first
      textAreaRef.current.style.height = "auto";
      // Then set it to scrollHeight to expand, with a max height
      const maxHeight = 100; // Maximum height in pixels
      const newHeight = Math.min(textAreaRef.current.scrollHeight, maxHeight);
      textAreaRef.current.style.height = newHeight + "px";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter") {
      if (e.shiftKey) {
        e.preventDefault();
        setInput((prev) => prev + "\n");
        // After adding a newline, adjust the height
        requestAnimationFrame(autoResize);
      } else {
        e.preventDefault();
        onSend();
        // Reset input and shrink
        setTimeout(() => {
          if (textAreaRef.current) {
            textAreaRef.current.style.height = "auto";
          }
        }, 0);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // auto-resize after user types
    autoResize();
  };

  return (
    <div className={`bottom-bar ${className}`}>
      <div className="chat-bubble">
        <div className="chat-bubble-icon">
          <img src={logoIcon} alt="Chat Icon" className="chat-icon-img" />
        </div>
        <textarea
          ref={textAreaRef}
          className="chat-bubble-textarea"
          placeholder={className.includes("centered-bottom-bar") ? "Ask anything" : "Start designing with ForgeMind..."}
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button className="chat-bubble-send-btn" onClick={onSend}>
          &#9658;
        </button>
      </div>
    </div>
  );
};

export default BottomBar;
