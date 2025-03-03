import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import BottomBar from "./components/BottomBar";
import ConnectCADModal from "./components/ConnectCADModal";
import OptimizeModal from "./components/OptimizeModal";
import RefineModal from "./components/RefineModal";
import RelationsModal from "./components/RelationsModal";
import { sendPrompt } from "./api";
import Header from "../components/layout/Header";

// Import modular CSS
import "./styles/reset.css";
import "./styles/layout.css";
import "./styles/buttons.css";
import "./styles/ChatWindow.css";
import "./styles/BottomBar.css";
import "./styles/modal.css";
import "./styles/Sidebar.css";
import "./styles/Header.css";

import fullLogo from "./assets/full_logo.png";
import logoIcon from "./assets/logo_icon.png";
import { Chat, Message } from "./types";

const OPENAI_API_KEY = process.env.REACT_APP_OPENAI_API_KEY;
const MODEL = "gpt-4o";

interface AppProps {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
}

const App: React.FC<AppProps> = ({ onToggleSidebar, sidebarOpen }) => {
  const [chats, setChats] = useState<Chat[]>([{ name: "Chat 1", messages: [] }]);
  const [activeChatIndex, setActiveChatIndex] = useState<number>(0);
  const [input, setInput] = useState<string>("");

  const [showCADPopup, setShowCADPopup] = useState<boolean>(false);
  const [showOptimizeModal, setShowOptimizeModal] = useState<boolean>(false);
  const [optimizeStep, setOptimizeStep] = useState<number>(1);
  const [constraintsInput, setConstraintsInput] = useState<string>("");
  const [showRefineModal, setShowRefineModal] = useState<boolean>(false);
  const [refineStep, setRefineStep] = useState<number>(1);
  const [showRelationsModal, setShowRelationsModal] = useState<boolean>(false);
  const [relationsStep, setRelationsStep] = useState<number>(1);
  const [relationChoice, setRelationChoice] = useState<string>("");
  const [otherText, setOtherText] = useState<string>("");

  const [chosenCAD, setChosenCAD] = useState<string>("");
  const [customCAD, setCustomCAD] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Use optional chaining to safely access messages
  const showLogo = chats[activeChatIndex]?.messages?.length > 0;
  const containerClass = sidebarOpen ? "app-container sidebar-open" : "app-container";

  function handleNewChat() {
    if (isLoading) {
      console.warn("Cannot create a new chat while AI is still reasoning.");
      return; // Prevent creating a new chat if a response is pending
    }

    // 1. Collect the numeric suffixes from all *visible* chats (Chat X).
    const usedNumbers: number[] = [];
    for (const chat of chats) {
      // Skip hidden chats
      if (chat.visible === false) continue;
  
      // Parse out the number if it matches "Chat X"
      const match = chat.name.match(/^Chat\s+(\d+)$/);
      if (match) {
        usedNumbers.push(parseInt(match[1], 10));
      }
    }
  
    // 2. Sort them
    usedNumbers.sort((a, b) => a - b);
  
    // 3. Find the smallest missing number, starting at 1
    let nextNumber = 1;
    for (const num of usedNumbers) {
      if (num === nextNumber) {
        nextNumber++;
      } else if (num > nextNumber) {
        // We found a gap, so break
        break;
      }
    }
  
    // 4. Create the new chat using that number
    const newChat: Chat = { name: `Chat ${nextNumber}`, messages: [] };
    setChats([...chats, newChat]);
    setActiveChatIndex(chats.length);
  }
  

  async function handleSend() {
    const text = input.trim();
    if (!text) return;

    const userMsg: Message = { role: "user", content: text };
    const updatedChats = [...chats];
    // Ensure we have a valid active chat before updating
    if (!updatedChats[activeChatIndex]) return;
    updatedChats[activeChatIndex] = {
      ...updatedChats[activeChatIndex],
      messages: [...updatedChats[activeChatIndex].messages, userMsg],
    };
    setChats(updatedChats);
    setInput("");

    setIsLoading(true);

    try {
      const response = await sendPrompt(text, "c2e9c803-41aa-4073-8b9d-f67b8cabfe9b");
      const assistantReply = response.response;

      const isScript =
        assistantReply.includes("function") ||
        assistantReply.includes("import") ||
        assistantReply.includes("const ") ||
        assistantReply.includes("let ") ||
        assistantReply.includes("var ");

      const finalReply = isScript
        ? "Done, do you need anything else?"
        : assistantReply;

      const assistantMsg: Message = { role: "assistant", content: finalReply };

      const finalChats = [...updatedChats];
      finalChats[activeChatIndex] = {
        ...finalChats[activeChatIndex],
        messages: [...finalChats[activeChatIndex].messages, assistantMsg],
      };
      setChats(finalChats);
    } catch (err) {
      console.error("API error:", err);
      const errorMsg: Message = { role: "assistant", content: "Sorry, something went wrong." };
      const finalChats = [...updatedChats];
      finalChats[activeChatIndex] = {
        ...finalChats[activeChatIndex],
        messages: [...finalChats[activeChatIndex].messages, errorMsg],
      };
      setChats(finalChats);
    } finally {
      setIsLoading(false);
    }
  }

  // Modal handlers
  const handleOpenCADPopup = () => setShowCADPopup(true);
  const handleCloseCADPopup = () => setShowCADPopup(false);

  const handleOptimizeClick = () => {
    setShowOptimizeModal(true);
    setOptimizeStep(1);
    setConstraintsInput("");
  };

  const handleOptimizeSubmitUpload = () => setOptimizeStep(2);
  const handleOptimizeSubmitConstraints = () => setOptimizeStep(3);
  const handleCancelOptimize = () => {
    setShowOptimizeModal(false);
    setOptimizeStep(1);
    setConstraintsInput("");
  };

  const handleRefineClick = () => {
    setShowRefineModal(true);
    setRefineStep(1);
  };

  const handleRefineSubmitSurfaces = () => setRefineStep(2);
  const handleCancelRefine = () => {
    setShowRefineModal(false);
    setRefineStep(1);
  };

  const handleRelationsClick = () => {
    setShowRelationsModal(true);
    setRelationsStep(1);
  };

  const handleRelationsSubmitParts = () => setRelationsStep(2);
  const handleRelationsSubmitBodyOrAssembly = () => setRelationsStep(3);
  const handleCancelRelations = () => {
    setShowRelationsModal(false);
    setRelationsStep(1);
  };

  const handleSelectCAD = (cad: string) => {
    if (cad === "Other") {
      setChosenCAD("Other");
      setCustomCAD("");
    } else {
      setChosenCAD(cad);
      setCustomCAD("");
    }
    setShowCADPopup(false);
  };

  const handleDisconnectCAD = () => {
    setChosenCAD("");
    setCustomCAD("");
  };

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
    // Map over chats and set visible to false for the selected chat
    const updatedChats = chats.map((chat, i) =>
      i === index ? { ...chat, visible: false } : chat
    );
    setChats(updatedChats);

    // If the active chat is being hidden, update activeChatIndex to the first visible chat (if any)
    if (index === activeChatIndex) {
      const firstVisibleIndex = updatedChats.findIndex(chat => chat.visible !== false);
      if (firstVisibleIndex >= 0) {
        setActiveChatIndex(firstVisibleIndex);
      } else {
        // If no chat is visible, optionally create a new default chat
        const newChat: Chat = { name: "Chat 1", messages: [] };
        setChats([newChat]);
        setActiveChatIndex(0);
      }
    }
  }

  return (
    <div className="app-wrapper">
      <div className={sidebarOpen ? "sidebar open" : "sidebar closed"}>
        {sidebarOpen && (
          <Sidebar
            chats={chats}
            activeChatIndex={activeChatIndex}
            setActiveChatIndex={setActiveChatIndex}
            onNewChat={handleNewChat}
            onDeleteChat={handleDeleteChat}
            onOptimize={handleOptimizeClick}
            onRefine={handleRefineClick}
            onRelations={handleRelationsClick}
            onSuggestCAD={handleSuggestCAD}
            onCrashAnalysis={handleCrashAnalysis}
            isLoading={isLoading}
          />
        )}
      </div>

      <div className={containerClass} style={{ marginTop: "50px" }}>
        <ChatWindow
          chats={chats}
          activeChatIndex={activeChatIndex}
          fullLogo={fullLogo}
          isLoading={isLoading}
        />

        <BottomBar
          input={input}
          setInput={setInput}
          onSend={handleSend}
          logoIcon={logoIcon}
        />
      </div>

      {showCADPopup && (
        <ConnectCADModal
          onSelectCAD={(cad) => {
            setChosenCAD(cad);
            setShowCADPopup(false);
          }}
          onClose={() => setShowCADPopup(false)}
        />
      )}

      {showOptimizeModal && (
        <OptimizeModal
          step={optimizeStep}
          constraintsInput={constraintsInput}
          setConstraintsInput={setConstraintsInput}
          onNextStep={optimizeStep === 1 ? handleOptimizeSubmitUpload : handleOptimizeSubmitConstraints}
          onCancel={handleCancelOptimize}
        />
      )}

      {showRefineModal && (
        <RefineModal
          step={refineStep}
          onNextStep={handleRefineSubmitSurfaces}
          onCancel={handleCancelRefine}
        />
      )}

      {showRelationsModal && (
        <RelationsModal
          step={relationsStep}
          relationChoice={relationChoice}
          otherText={otherText}
          setRelationChoice={setRelationChoice}
          setOtherText={setOtherText}
          onNextStep={relationsStep === 1 ? handleRelationsSubmitParts : handleRelationsSubmitBodyOrAssembly}
          onCancel={handleCancelRelations}
        />
      )}
    </div>
  );
};

export default App;
