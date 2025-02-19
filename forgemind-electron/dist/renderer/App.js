"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
// src/renderer/App.tsx
const react_1 = require("react");
const Sidebar_1 = __importDefault(require("./components/Sidebar"));
const ChatWindow_1 = __importDefault(require("./components/ChatWindow"));
const BottomBar_1 = __importDefault(require("./components/BottomBar"));
const ConnectCADModal_1 = __importDefault(require("./components/ConnectCADModal"));
const OptimizeModal_1 = __importDefault(require("./components/OptimizeModal"));
const RefineModal_1 = __importDefault(require("./components/RefineModal"));
const RelationsModal_1 = __importDefault(require("./components/RelationsModal"));
// Import modular CSS
require("./styles/reset.css");
require("./styles/layout.css");
require("./styles/buttons.css");
require("./styles/ChatWindow.css");
require("./styles/BottomBar.css");
require("./styles/modal.css");
const full_logo_png_1 = __importDefault(require("./assets/full_logo.png"));
const logo_icon_png_1 = __importDefault(require("./assets/logo_icon.png"));
const OPENAI_API_KEY = process.env.REACT_APP_OPENAI_API_KEY;
const MODEL = "gpt-4o";
const App = () => {
    const [sidebarOpen, setSidebarOpen] = (0, react_1.useState)(false);
    const [chats, setChats] = (0, react_1.useState)([{ name: "Chat 1", messages: [] }]);
    const [activeChatIndex, setActiveChatIndex] = (0, react_1.useState)(0);
    const [input, setInput] = (0, react_1.useState)("");
    const [showCADPopup, setShowCADPopup] = (0, react_1.useState)(false);
    const [showOptimizeModal, setShowOptimizeModal] = (0, react_1.useState)(false);
    const [optimizeStep, setOptimizeStep] = (0, react_1.useState)(1);
    const [constraintsInput, setConstraintsInput] = (0, react_1.useState)("");
    const [showRefineModal, setShowRefineModal] = (0, react_1.useState)(false);
    const [refineStep, setRefineStep] = (0, react_1.useState)(1);
    const [showRelationsModal, setShowRelationsModal] = (0, react_1.useState)(false);
    const [relationsStep, setRelationsStep] = (0, react_1.useState)(1);
    const [relationChoice, setRelationChoice] = (0, react_1.useState)("");
    const [otherText, setOtherText] = (0, react_1.useState)("");
    const [chosenCAD, setChosenCAD] = (0, react_1.useState)("");
    const [customCAD, setCustomCAD] = (0, react_1.useState)("");
    const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
    const containerClass = sidebarOpen ? "app-container sidebar-open" : "app-container";
    const currentChat = chats[activeChatIndex];
    function handleNewChat() {
        const newChat = { name: `Chat ${chats.length + 1}`, messages: [] };
        setChats((prev) => [...prev, newChat]);
        setActiveChatIndex(chats.length);
    }
    function handleSend() {
        var _a, _b, _c;
        return __awaiter(this, void 0, void 0, function* () {
            const text = input.trim();
            if (!text)
                return;
            const userMsg = { role: "user", content: text };
            const updatedChats = [...chats];
            updatedChats[activeChatIndex] = Object.assign(Object.assign({}, currentChat), { messages: [...currentChat.messages, userMsg] });
            setChats(updatedChats);
            setInput("");
            try {
                const cadInfo = chosenCAD
                    ? ` You are currently connected to ${chosenCAD === "Other" && customCAD ? customCAD : chosenCAD}.`
                    : " You are not currently connected to any CAD software.";
                const res = yield fetch("https://api.openai.com/v1/chat/completions", {
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
                const data = yield res.json();
                const aiReply = ((_c = (_b = (_a = data.choices) === null || _a === void 0 ? void 0 : _a[0]) === null || _b === void 0 ? void 0 : _b.message) === null || _c === void 0 ? void 0 : _c.content) || "No response from AI.";
                const assistantMsg = { role: "assistant", content: aiReply };
                const finalChats = [...updatedChats];
                finalChats[activeChatIndex] = Object.assign(Object.assign({}, updatedChats[activeChatIndex]), { messages: [...updatedChats[activeChatIndex].messages, assistantMsg] });
                setChats(finalChats);
            }
            catch (err) {
                console.error("OpenAI API Error:", err);
                const errorMsg = { role: "assistant", content: "Sorry, something went wrong." };
                const finalChats = [...updatedChats];
                finalChats[activeChatIndex] = Object.assign(Object.assign({}, updatedChats[activeChatIndex]), { messages: [...updatedChats[activeChatIndex].messages, errorMsg] });
                setChats(finalChats);
            }
        });
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
    const handleSelectCAD = (cad) => {
        if (cad === "Other") {
            setChosenCAD("Other");
            setCustomCAD("");
        }
        else {
            setChosenCAD(cad);
            setCustomCAD("");
        }
        setShowCADPopup(false);
    };
    return ((0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "app-wrapper" }, { children: [(0, jsx_runtime_1.jsx)(Sidebar_1.default, { chats: chats, activeChatIndex: activeChatIndex, setActiveChatIndex: setActiveChatIndex, onNewChat: handleNewChat }), (0, jsx_runtime_1.jsxs)("div", Object.assign({ className: containerClass }, { children: [(0, jsx_runtime_1.jsx)("button", Object.assign({ className: "menu-btn", onClick: toggleSidebar }, { children: "\u2630" })), (0, jsx_runtime_1.jsx)("div", Object.assign({ className: "cad-connection-container" }, { children: !chosenCAD ? ((0, jsx_runtime_1.jsx)("button", Object.assign({ className: "connect-cad-btn", onClick: handleOpenCADPopup }, { children: "Connect" }))) : ((0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "chosen-cad-controls" }, { children: [(0, jsx_runtime_1.jsx)("button", Object.assign({ className: "chosen-cad-btn", onClick: handleOpenCADPopup }, { children: chosenCAD === "Other" && customCAD ? customCAD : chosenCAD })), (0, jsx_runtime_1.jsx)("button", Object.assign({ className: "disconnect-cad-btn", onClick: () => {
                                        setChosenCAD("");
                                        setCustomCAD("");
                                    } }, { children: "Disconnect" }))] }))) })), (0, jsx_runtime_1.jsx)(ChatWindow_1.default, { chats: chats, activeChatIndex: activeChatIndex, fullLogo: full_logo_png_1.default }), (0, jsx_runtime_1.jsx)(BottomBar_1.default, { input: input, setInput: setInput, onSend: handleSend, logoIcon: logo_icon_png_1.default, onOptimize: handleOptimizeClick, onRefine: handleRefineClick, onRelations: handleRelationsClick })] })), showCADPopup && ((0, jsx_runtime_1.jsx)(ConnectCADModal_1.default, { onSelectCAD: handleSelectCAD, onClose: handleCloseCADPopup })), showOptimizeModal && ((0, jsx_runtime_1.jsx)(OptimizeModal_1.default, { step: optimizeStep, constraintsInput: constraintsInput, setConstraintsInput: setConstraintsInput, onNextStep: optimizeStep === 1 ? handleOptimizeSubmitUpload : handleOptimizeSubmitConstraints, onCancel: handleCancelOptimize })), showRefineModal && ((0, jsx_runtime_1.jsx)(RefineModal_1.default, { step: refineStep, onNextStep: handleRefineSubmitSurfaces, onCancel: handleCancelRefine })), showRelationsModal && ((0, jsx_runtime_1.jsx)(RelationsModal_1.default, { step: relationsStep, relationChoice: relationChoice, otherText: otherText, setRelationChoice: setRelationChoice, setOtherText: setOtherText, onNextStep: relationsStep === 1 ? handleRelationsSubmitParts : handleRelationsSubmitBodyOrAssembly, onCancel: handleCancelRelations }))] })));
};
exports.default = App;
