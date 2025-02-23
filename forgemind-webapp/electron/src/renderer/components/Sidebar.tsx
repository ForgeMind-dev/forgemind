import React from "react";
import { Chat } from "../types";
import "../styles/Sidebar.css";
import trashBinIcon from "../assets/trash_bin.png"; // ensure this file exists

interface SidebarProps {
  chats: Chat[];
  activeChatIndex: number;
  setActiveChatIndex: (index: number) => void;
  onNewChat: () => void;
  onOptimize: () => void;
  onRefine: () => void;
  onRelations: () => void;
  onSuggestCAD: () => void;
  onCrashAnalysis: () => void;
  onDeleteChat: (index: number) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  chats,
  activeChatIndex,
  setActiveChatIndex,
  onNewChat,
  onOptimize,
  onRefine,
  onRelations,
  onSuggestCAD,
  onCrashAnalysis,
  onDeleteChat,
}) => {
  // Only render chats that are visible (or where visible is undefined)
  const visibleChats = chats.filter(chat => chat.visible !== false);

  return (
    <div className="sidebar">
      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>

      <h2>Chats</h2>
      <ul>
        {visibleChats.map((chat, idx) => (
          <li
            key={idx}
            className={idx === activeChatIndex ? "active-chat" : ""}
          >
            <div className="chat-item">
              <span onClick={() => setActiveChatIndex(idx)} className="chat-name">
                {chat.name}
              </span>
              <button
                className="delete-chat-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  // Find the original index in the full chats array
                  const originalIndex = chats.findIndex(c => c === chat);
                  onDeleteChat(originalIndex);
                }}
              >
                <img src={trashBinIcon} alt="Delete Chat" className="delete-icon" />
              </button>
            </div>
          </li>
        ))}
      </ul>

      <h2>Quick Tools</h2>
      <div className="quick-actions">
        <button onClick={onSuggestCAD}>Suggest a CAD Tool</button>
        <button onClick={onOptimize}>Optimize Tolerances</button>
        <button onClick={onRefine}>Refine Curved Surfaces</button>
        <button onClick={onCrashAnalysis}>Run Crash Analysis</button>
        <button onClick={onRelations}>View Part Relations</button>
      </div>
    </div>
  );
};

export default Sidebar;
