"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const react_markdown_1 = __importDefault(require("react-markdown"));
const ChatWindow = ({ chats, activeChatIndex, fullLogo, }) => {
    const currentChat = chats[activeChatIndex];
    if (currentChat.messages.length === 0) {
        return ((0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "center-content" }, { children: [(0, jsx_runtime_1.jsx)("img", { src: fullLogo, alt: "ForgeMind Logo", className: "main-logo" }), (0, jsx_runtime_1.jsx)("h1", { children: "What do you want to design today?" })] })));
    }
    return ((0, jsx_runtime_1.jsx)("div", Object.assign({ className: "messages-container" }, { children: currentChat.messages.map((msg, idx) => msg.role === "user" ? ((0, jsx_runtime_1.jsx)("div", Object.assign({ className: "msg user-msg" }, { children: msg.content }), idx)) : ((0, jsx_runtime_1.jsx)("div", Object.assign({ className: "msg ai-msg" }, { children: (0, jsx_runtime_1.jsx)(react_markdown_1.default, { children: msg.content }) }), idx))) })));
};
exports.default = ChatWindow;
