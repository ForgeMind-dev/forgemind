// src/renderer/components/RelationsModal.tsx

import React from 'react';

interface RelationsModalProps {
  step: number;
  relationChoice: string;
  otherText: string;
  setRelationChoice: (value: string) => void;
  setOtherText: (value: string) => void;
  onNextStep: () => void;
  onCancel: () => void;
}

const RelationsModal: React.FC<RelationsModalProps> = ({
  step,
  relationChoice,
  otherText,
  setRelationChoice,
  setOtherText,
  onNextStep,
  onCancel,
}) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {step === 1 && (
          <>
            <h2>View Part Relations</h2>
            <p>Which parts do you want to see relations for? Choose from your CAD please!</p>
            <div className="modal-button-row">
              <button className="primary-modal-btn" onClick={onNextStep}>
                Submit
              </button>
            </div>
          </>
        )}
        {step === 2 && (
          <>
            <h2>View Part Relations</h2>
            <p>Do you want to see relations in the body, in the assembly, or Other?</p>
            <div style={{ margin: "1rem 0" }}>
              <label style={{ display: "block", marginBottom: "8px" }}>
                <input
                  type="radio"
                  name="relationChoice"
                  value="body"
                  checked={relationChoice === "body"}
                  onChange={(e) => setRelationChoice(e.target.value)}
                />
                {" "}In the body
              </label>
              <label style={{ display: "block", marginBottom: "8px" }}>
                <input
                  type="radio"
                  name="relationChoice"
                  value="assembly"
                  checked={relationChoice === "assembly"}
                  onChange={(e) => setRelationChoice(e.target.value)}
                />
                {" "}In the assembly
              </label>
              <label style={{ display: "block" }}>
                <input
                  type="radio"
                  name="relationChoice"
                  value="other"
                  checked={relationChoice === "other"}
                  onChange={(e) => setRelationChoice(e.target.value)}
                />
                {" "}Other
              </label>
              {relationChoice === "other" && (
                <textarea
                  rows={2}
                  value={otherText}
                  onChange={(e) => setOtherText(e.target.value)}
                  placeholder="Please explain..."
                  style={{ width: "100%", marginTop: "8px" }}
                />
              )}
            </div>
            <div className="modal-button-row">
              <button className="primary-modal-btn" onClick={onNextStep}>
                Send
              </button>
            </div>
          </>
        )}
        {step === 3 && (
          <>
            <h2>View Part Relations</h2>
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

export default RelationsModal;
