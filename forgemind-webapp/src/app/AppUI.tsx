import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import BottomBar from "./components/BottomBar";
import { sendPrompt } from "./api";
import Header from "../components/layout/Header";

// Import modular CSS
import "./styles/reset.css";
import "./styles/layout.css";
import "./styles/ChatWindow.css";
import "./styles/BottomBar.css";
import "./styles/Sidebar.css";

import fullLogo from "./assets/full_logo.png";
import logoIcon from "./assets/logo_icon.png";
import { Chat, Message } from "./types";

interface AppProps {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
}

const App: React.FC<AppProps> = ({ onToggleSidebar, sidebarOpen }) => {
  const [chats, setChats] = useState<Chat[]>([{ name: "Chat 1", messages: [] }]);
  const [activeChatIndex, setActiveChatIndex] = useState<number>(0);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Use optional chaining to safely access messages
  const showLogo = chats[activeChatIndex]?.messages?.length > 0;
  const containerClass = sidebarOpen ? "app-container sidebar-open" : "app-container";

  function handleNewChat() {
    if (isLoading) {
      return;
    }

    setChats([...chats, { name: `Chat ${chats.length + 1}`, messages: [] }]);
    setActiveChatIndex(chats.length);
    setInput("");
  }

  async function handleSend() {
    if (!input.trim() || isLoading) {
      return;
    }

    // Create new message and add to active chat
    const newMessage: Message = {
      role: "user",
      content: input,
    };

    const updatedChats = [...chats];
    updatedChats[activeChatIndex].messages.push(newMessage);

    // Clear input field
    setInput("");
    setIsLoading(true);

    // Update state to reflect user message
    setChats(updatedChats);

    try {
      // Send to backend API and get response
      // Pass the current chat's threadId (if any) to the API call.
      const aiResponse = await sendPrompt(input, "c2e9c803-41aa-4073-8b9d-f67b8cabfe9b", updatedChats[activeChatIndex].threadId);

      // If the chat didn't already have a threadId, store the new one.
      if (!updatedChats[activeChatIndex].threadId && aiResponse.thread_id) {
        updatedChats[activeChatIndex].threadId = aiResponse.thread_id;
      }

      // Create AI message
      const aiMessage: Message = {
        role: "assistant",
        content: aiResponse?.response || "Sorry, there was an error processing your request.",
      };

      // Add AI message to chat
      updatedChats[activeChatIndex].messages.push(aiMessage);

      // Update state
      setChats([...updatedChats]);
    } catch (error) {
      console.error("Error calling API:", error);

      // Create error message
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };

      // Add error message to chat
      updatedChats[activeChatIndex].messages.push(errorMessage);

      // Update state
      setChats([...updatedChats]);
    } finally {
      setIsLoading(false);
    }
  }

  // New Quick Tool Handlers
  const handleSuggestCAD = () => {
    console.log("Suggest a CAD Tool clicked");
    // Add your logic here
  };

  const handleCrashAnalysis = () => {
    console.log("Run Crash Analysis clicked");
    // Add your logic here
  };

  function handleDeleteChat(index: number) {
    // Remove the chat from the list
    const updatedChats = chats.filter((_, i) => i !== index);

    if (updatedChats.length === 0) {
      // If we deleted the last chat, create a new empty one
      setChats([{ name: "Chat 1", messages: [] }]);
      setActiveChatIndex(0);
    } else {
      setChats(updatedChats);
      // Adjust active index if needed
      if (index === activeChatIndex) {
        // If we deleted the active chat, set active to the previous one
        // or the first one if we deleted the first chat
        setActiveChatIndex(index === 0 ? 0 : index - 1);
      } else if (index < activeChatIndex) {
        // If we deleted a chat before the active one, decrement the active index
        setActiveChatIndex(activeChatIndex - 1);
      }
      // If we deleted a chat after the active one, no change to active index is needed
    }
  }

  // These empty handlers are placeholders for the removed modals
  const handleOptimize = () => console.log("Optimize feature removed");
  const handleRefine = () => console.log("Refine feature removed");
  const handleRelations = () => console.log("Relations feature removed");

  return (
    <div className="app-wrapper">
      <Header onToggleSidebar={onToggleSidebar} />
      
      <div className={containerClass}>
        <div className={sidebarOpen ? "sidebar" : "sidebar closed"}>
          <Sidebar
            chats={chats}
            activeChatIndex={activeChatIndex}
            setActiveChatIndex={setActiveChatIndex}
            onNewChat={handleNewChat}
            onDeleteChat={handleDeleteChat}
            onOptimize={handleOptimize}
            onRefine={handleRefine}
            onRelations={handleRelations}
            onSuggestCAD={handleSuggestCAD}
            onCrashAnalysis={handleCrashAnalysis}
            isLoading={isLoading}
          />
        </div>
        
        <ChatWindow
          chats={chats}
          activeChatIndex={activeChatIndex}
          isLoading={isLoading}
          fullLogo={fullLogo}
        />
        
        <BottomBar
          input={input}
          setInput={setInput}
          onSend={handleSend}
          logoIcon={logoIcon}
          className={chats[activeChatIndex]?.messages?.length === 0 ? "centered-bottom-bar" : ""}
        />
      </div>
    </div>
  );
};

export default App;
