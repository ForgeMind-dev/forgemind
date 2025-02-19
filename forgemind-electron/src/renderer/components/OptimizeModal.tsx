// src/renderer/components/OptimizeModal.tsx

import React from 'react';

interface OptimizeModalProps {
  step: number;
  constraintsInput: string;
  setConstraintsInput: (value: string) => void;
  onNextStep: () => void;
  onCancel: () => void;
}

const OptimizeModal: React.FC<OptimizeModalProps> = ({
  step,
  constraintsInput,
  setConstraintsInput,
  onNextStep,
  onCancel,
}) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {step === 1 && (
          <>
            <h2>Optimize Tolerances</h2>
            <p>Upload your engineering drawings or connect to CAD for cloud access.</p>
            <div style={{ marginBottom: "1rem" }}>
              <input type="file" />
            </div>
            <div className="modal-button-row">
              <button className="primary-modal-btn" onClick={onNextStep}>
                Submit
              </button>
            </div>
          </>
        )}
        {step === 2 && (
          <>
            <h2>Optimize Tolerances</h2>
            <p>Any critical features or tolerances that can't change?</p>
            <textarea
              rows={3}
              value={constraintsInput}
              onChange={(e) => setConstraintsInput(e.target.value)}
              style={{ width: "100%", marginBottom: "1rem" }}
            />
            <div className="modal-button-row">
              <button className="primary-modal-btn" onClick={onNextStep}>
                Send
              </button>
            </div>
          </>
        )}
        {step === 3 && (
          <>
            <h2>Optimize Tolerances</h2>
            <p>Running analysis...</p>
            <div className="spinner" />
            <div className="modal-button-row">
              <button className="close-modal-btn" onClick={onCancel}>
                Cancel
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default OptimizeModal;
