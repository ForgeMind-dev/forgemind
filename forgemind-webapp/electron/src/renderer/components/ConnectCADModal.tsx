// src/renderer/components/ConnectCADModal.tsx

import React from 'react';

interface ConnectCADModalProps {
  onSelectCAD: (cad: string) => void;
  onClose: () => void;
}

const ConnectCADModal: React.FC<ConnectCADModalProps> = ({ onSelectCAD, onClose }) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Connect to CAD</h2>
        <p>Choose a CAD software:</p>
        <div className="cad-grid">
          <div className="cad-card" onClick={() => onSelectCAD("forge-catia_v1")}>
            CATIA
          </div>
          <div className="cad-card" onClick={() => onSelectCAD("Solidworks")}>
            Solidworks
          </div>
          <div className="cad-card" onClick={() => onSelectCAD("NX")}>
            NX
          </div>
          <div className="cad-card" onClick={() => onSelectCAD("Other")}>
            Other
          </div>
        </div>
        <button className="close-modal-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default ConnectCADModal;
