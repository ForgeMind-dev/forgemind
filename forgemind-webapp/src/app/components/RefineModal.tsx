// src/renderer/components/RefineModal.tsx

import React from 'react';

interface RefineModalProps {
  step: number;
  onNextStep: () => void;
  onCancel: () => void;
}

const RefineModal: React.FC<RefineModalProps> = ({ step, onNextStep, onCancel }) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {step === 1 && (
          <>
            <h2>Refine Curved Surfaces</h2>
            <p>
              Which surfaces do you want to refine? Our software automatically understands your CAD surfaces.
            </p>
            <div className="modal-button-row">
              <button className="primary-modal-btn" onClick={onNextStep}>
                Submit
              </button>
            </div>
          </>
        )}
        {step === 2 && (
          <>
            <h2>Refine Curved Surfaces</h2>
            <p>Refining surfaces...</p>
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

export default RefineModal;
