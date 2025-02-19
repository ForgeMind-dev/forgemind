"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const Sidebar = ({ chats, activeChatIndex, setActiveChatIndex, onNewChat, }) => {
    return ((0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "sidebar" }, { children: [(0, jsx_runtime_1.jsx)("button", Object.assign({ onClick: onNewChat }, { children: "New Chat" })), (0, jsx_runtime_1.jsx)("ul", { children: chats.map((chat, index) => ((0, jsx_runtime_1.jsx)("li", Object.assign({ className: activeChatIndex === index ? 'active' : '', onClick: () => setActiveChatIndex(index) }, { children: chat.name }), index))) })] })));
};
exports.default = Sidebar;
