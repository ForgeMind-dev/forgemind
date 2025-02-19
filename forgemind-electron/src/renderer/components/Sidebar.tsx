import React from "react";
import { Chat } from "../types";
import "../styles/Sidebar.css";

interface SidebarProps {
  chats: Chat[];
  activeChatIndex: number;
  setActiveChatIndex: (index: number) => void;
  onNewChat: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  chats,
  activeChatIndex,
  setActiveChatIndex,
  onNewChat,
}) => {
  return (
    <div className="sidebar">
      {/* Button for new chat */}
      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>

      <h2>Chats</h2>
      <ul>
        {chats.map((chat, idx) => (
          <li
            key={idx}
            className={idx === activeChatIndex ? "active-chat" : ""}
            onClick={() => setActiveChatIndex(idx)}
          >
            {chat.name}
          </li>
        ))}
      </ul>

      <h2>Optimization Tools</h2>
      <ul>
        <li>Tolerance Optimization</li>
        <li>Assembly Analysis</li>
      </ul>
    </div>
  );
};

export default Sidebar;
