// src/renderer/App.tsx

import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import BottomBar from "./components/BottomBar";
import ConnectCADModal from "./components/ConnectCADModal";
import OptimizeModal from "./components/OptimizeModal";
import RefineModal from "./components/RefineModal";
import RelationsModal from "./components/RelationsModal";

// Import modular CSS
import "./styles/reset.css";
import "./styles/layout.css";
import "./styles/buttons.css";
import "./styles/ChatWindow.css";
import "./styles/BottomBar.css";
import "./styles/modal.css";
import "./styles/Sidebar.css";

import fullLogo from "./assets/full_logo.png";
import logoIcon from "./assets/logo_icon.png";
import { Chat, Message } from "./types";

const OPENAI_API_KEY = process.env.REACT_APP_OPENAI_API_KEY;
const MODEL = "gpt-4o";

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
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

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  const containerClass = sidebarOpen ? "app-container sidebar-open" : "app-container";

  const currentChat = chats[activeChatIndex];

  function handleNewChat() {
    const newChat: Chat = { name: `Chat ${chats.length + 1}`, messages: [] };
    setChats((prev) => [...prev, newChat]);
    setActiveChatIndex(chats.length);
  }

  async function handleSend() {
    const text = input.trim();
    if (!text) return;

    const userMsg: Message = { role: "user", content: text };
    const updatedChats = [...chats];
    updatedChats[activeChatIndex] = {
      ...currentChat,
      messages: [...currentChat.messages, userMsg],
    };
    setChats(updatedChats);
    setInput("");

    try {
      const cadInfo = chosenCAD
        ? ` You are currently connected to ${chosenCAD === "Other" && customCAD ? customCAD : chosenCAD}.`
        : " You are not currently connected to any CAD software.";

      const res = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: MODEL,
          messages: [
            {
              role: "system",
              content: `
                You are ForgeMind AI, a specialized mechanical and CAD design assistant. 
                ForgeMind AI includes its own wizards/features, such as:
                 • "Optimize Tolerances"
                 • "Refine Curved Surfaces"
                 • "View Part Relations"
                 • "Crash Analysis"
                These are built-in ForgeMind capabilities, not part of any external CAD software.

                The user can also connect to an external CAD (like CATIA, NX, SolidWorks, Fusion 360).
                You may reference these CAD tools for specific modeling or simulation modules, 
                but please keep in mind that ForgeMind wizards (e.g. "Refine Curved Surfaces") 
                are separate, internal ForgeMind features that integrate with whichever CAD is chosen.

                Currently: ${cadInfo}

                Always:
                 • Clarify the user's goals and constraints.
                 • Recommend relevant ForgeMind AI wizards or external CAD features, as needed.
                 • Provide step-by-step design guidance or analysis steps.
                 • End with a question or prompt to encourage further discussion, 
                   unless it's clearly the final request.
              `,
            },
            ...updatedChats[activeChatIndex].messages,
          ],
        }),
      });

      if (!res.ok) {
        throw new Error(`OpenAI API error: ${res.status}`);
      }

      const data = await res.json();
      const aiReply = data.choices?.[0]?.message?.content || "No response from AI.";
      const assistantMsg: Message = { role: "assistant", content: aiReply };

      const finalChats = [...updatedChats];
      finalChats[activeChatIndex] = {
        ...updatedChats[activeChatIndex],
        messages: [...updatedChats[activeChatIndex].messages, assistantMsg],
      };
      setChats(finalChats);
    } catch (err) {
      console.error("OpenAI API Error:", err);
      const errorMsg: Message = { role: "assistant", content: "Sorry, something went wrong." };
      const finalChats = [...updatedChats];
      finalChats[activeChatIndex] = {
        ...updatedChats[activeChatIndex],
        messages: [...updatedChats[activeChatIndex].messages, errorMsg],
      };
      setChats(finalChats);
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

  return (
    <div className="app-wrapper">
      <Sidebar
        chats={chats}
        activeChatIndex={activeChatIndex}
        setActiveChatIndex={setActiveChatIndex}
        onNewChat={handleNewChat}
      />

      <div className={containerClass}>
        <button className="menu-btn" onClick={toggleSidebar}>
          &#9776;
        </button>
        <div className="cad-connection-container">
          {!chosenCAD ? (
            <button className="connect-cad-btn" onClick={handleOpenCADPopup}>
              Connect
            </button>
          ) : (
            <div className="chosen-cad-controls">
              <button className="chosen-cad-btn" onClick={handleOpenCADPopup}>
                {chosenCAD === "Other" && customCAD ? customCAD : chosenCAD}
              </button>
              <button
                className="disconnect-cad-btn"
                onClick={() => {
                  setChosenCAD("");
                  setCustomCAD("");
                }}
              >
                Disconnect
              </button>
            </div>
          )}
        </div>

        <ChatWindow chats={chats} activeChatIndex={activeChatIndex} fullLogo={fullLogo} />

        <BottomBar
          input={input}
          setInput={setInput}
          onSend={handleSend}
          logoIcon={logoIcon}
          onOptimize={handleOptimizeClick}
          onRefine={handleRefineClick}
          onRelations={handleRelationsClick}
        />
      </div>

      {showCADPopup && (
        <ConnectCADModal
          onSelectCAD={handleSelectCAD}
          onClose={handleCloseCADPopup}
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
