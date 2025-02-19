"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const ConnectCADModal = ({ onSelectCAD, onClose }) => {
    return ((0, jsx_runtime_1.jsx)("div", Object.assign({ className: "modal-overlay" }, { children: (0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "modal-content" }, { children: [(0, jsx_runtime_1.jsx)("h2", { children: "Connect to CAD" }), (0, jsx_runtime_1.jsx)("p", { children: "Choose a CAD software:" }), (0, jsx_runtime_1.jsxs)("div", Object.assign({ className: "cad-grid" }, { children: [(0, jsx_runtime_1.jsx)("div", Object.assign({ className: "cad-card", onClick: () => onSelectCAD("CATIA") }, { children: "CATIA" })), (0, jsx_runtime_1.jsx)("div", Object.assign({ className: "cad-card", onClick: () => onSelectCAD("Solidworks") }, { children: "Solidworks" })), (0, jsx_runtime_1.jsx)("div", Object.assign({ className: "cad-card", onClick: () => onSelectCAD("NX") }, { children: "NX" })), (0, jsx_runtime_1.jsx)("div", Object.assign({ className: "cad-card", onClick: () => onSelectCAD("Other") }, { children: "Other" }))] })), (0, jsx_runtime_1.jsx)("button", Object.assign({ className: "close-modal-btn", onClick: onClose }, { children: "Close" }))] })) })));
};
exports.default = ConnectCADModal;
