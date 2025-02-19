"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const BottomBar = ({ input, setInput, onSend, logoIcon, onOptimize, onRefine, onRelations, }) => {
    const handleKeyDown = (e) => {
        if (e.key === "Enter")
            onSend();
    };
    return ((0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "bottom-bar" }, { children: [(0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "quick-actions" }, { children: [(0, jsx_runtime_1.jsx)("button", Object.assign({ className: "quick-pill" }, { children: "Suggest a CAD Tool" })), (0, jsx_runtime_1.jsx)("button", Object.assign({ className: "quick-pill", onClick: onOptimize }, { children: "Optimize Tolerances" })), (0, jsx_runtime_1.jsx)("button", Object.assign({ className: "quick-pill", onClick: onRefine }, { children: "Refine Curved Surfaces" })), (0, jsx_runtime_1.jsx)("button", Object.assign({ className: "quick-pill" }, { children: "Run Crash Analysis" })), (0, jsx_runtime_1.jsx)("button", Object.assign({ className: "quick-pill", onClick: onRelations }, { children: "View Part Relations" }))] })), (0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "chat-bubble" }, { children: [(0, jsx_runtime_1.jsx)("div", Object.assign({ className: "chat-bubble-icon" }, { children: (0, jsx_runtime_1.jsx)("img", { src: logoIcon, alt: "Chat Icon", className: "chat-icon-img" }) })), (0, jsx_runtime_1.jsx)("input", { className: "chat-bubble-input", placeholder: "Start building with ForgeMind...", value: input, onChange: (e) => setInput(e.target.value), onKeyDown: handleKeyDown }), (0, jsx_runtime_1.jsx)("button", Object.assign({ className: "chat-bubble-send-btn", onClick: onSend }, { children: "\u25BA" }))] }))] })));
};
exports.default = BottomBar;
