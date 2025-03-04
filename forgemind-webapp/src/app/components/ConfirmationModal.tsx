import React from 'react';
import '../styles/ConfirmationModal.css';

interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmButtonText: string;
  cancelButtonText: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  title,
  message,
  confirmButtonText,
  cancelButtonText,
  onConfirm,
  onCancel
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <div className="modal-header">
          <h2>{title}</h2>
        </div>
        <div className="modal-content">
          <p>{message}</p>
        </div>
        <div className="modal-actions">
          <button className="cancel-button" onClick={onCancel}>
            {cancelButtonText}
          </button>
          <button className="confirm-button" onClick={onConfirm}>
            {confirmButtonText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal; 