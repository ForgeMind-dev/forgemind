// src/renderer/App.tsx

import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import BottomBar from "./components/BottomBar";
import ConnectCADModal from "./components/ConnectCADModal";
import OptimizeModal from "./components/OptimizeModal";
import RefineModal from "./components/RefineModal";
import RelationsModal from "./components/RelationsModal";
import { createThread, sendPrompt, getThreads } from "./api";

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

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatIndex, setActiveChatIndex] = useState<number>(0);
  const [input, setInput] = useState<string>("");
  const [threadId, setThreadId] = useState<string>("");

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

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  const containerClass = sidebarOpen ? "app-container sidebar-open" : "app-container";

  const currentChat = chats[activeChatIndex];

  useEffect(() => {
    async function fetchThreads() {
      try {
        const threads = await getThreads("c2e9c803-41aa-4073-8b9d-f67b8cabfe9b");
        if (threads.length === 0) {
          const newThread = await createThread("c2e9c803-41aa-4073-8b9d-f67b8cabfe9b");
          const initialChat: Chat = { name: "Chat 1", messages: [], threadId: newThread.thread_id };
          console.log('FURGO new thread', newThread);
          setThreadId(newThread.thread_id);
          setChats([initialChat]);
          setActiveChatIndex(0);
        } else {
          // Map threads response to Chat type if necessary.
          setChats(threads);
          setActiveChatIndex(0);
        }
      } catch (err) {
        console.error(err);
      }
    }
    fetchThreads();
  }, []);

  async function handleNewChat() {
    const newThread = await createThread("c2e9c803-41aa-4073-8b9d-f67b8cabfe9b");
    const newChat: Chat = { name: `Chat ${chats.length + 1}`, messages: [], threadId: newThread.thread_id };
    setChats([...chats, newChat]);
    setActiveChatIndex(chats.length);
  }

  async function handleSend() {
    const text = input.trim();
    if (!text) return;

    const userMsg: Message = { role: "user", content: text };
    const updatedChats = [...chats];
    updatedChats[activeChatIndex] = {
      ...updatedChats[activeChatIndex],
      messages: [...updatedChats[activeChatIndex].messages ?? [], userMsg],
    };
    setChats(updatedChats);
    setInput("");

    setIsLoading(true);

    try {
      const response = await sendPrompt(text, "c2e9c803-41aa-4073-8b9d-f67b8cabfe9b", threadId);
      const assistantReply = response.response;

      // Check if the reply is a script
      const isScript =
        assistantReply.includes("function") ||
        assistantReply.includes("import") ||
        assistantReply.includes("const ") ||
        assistantReply.includes("let ") ||
        assistantReply.includes("var ");

      // Replace script with a friendly message
      const finalReply = isScript
        ? "Done, do you need anything else?"
        : assistantReply;

      const assistantMsg: Message = { role: "assistant", content: finalReply };

      // Append the assistant message to the updated chat
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

  return (
    <div className="app-wrapper">
      <Header
        onToggleSidebar={toggleSidebar}
        chosenCAD={chosenCAD}
        customCAD={customCAD}
        onConnectClick={handleOpenCADPopup}
        onDisconnectClick={handleDisconnectCAD}
      />

      <Sidebar
        chats={chats}
        activeChatIndex={activeChatIndex}
        setActiveChatIndex={setActiveChatIndex}
        onNewChat={handleNewChat}
      />

      <div className={containerClass} style={{ marginTop: "50px" }}>
        {chats.length && <ChatWindow
          chats={chats}
          activeChatIndex={activeChatIndex}
          fullLogo={fullLogo}
          isLoading={isLoading}
        />}

        <BottomBar
          input={input}
          setInput={setInput}
          onSend={handleSend}
          logoIcon={logoIcon}
          onOptimize={() => {
            setShowOptimizeModal(true);
            setOptimizeStep(1);
            setConstraintsInput("");
          }}
          onRefine={() => {
            setShowRefineModal(true);
            setRefineStep(1);
          }}
          onRelations={() => {
            setShowRelationsModal(true);
            setRelationsStep(1);
          }}
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
