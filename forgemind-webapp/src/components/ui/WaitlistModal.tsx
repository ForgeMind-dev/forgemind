import React, { useState } from 'react';
import { supabase } from '../../supabaseClient'; // Adjust path as needed
import './WaitlistModal.css';

interface WaitlistModalProps {
  onClose: () => void;
}

const WaitlistModal: React.FC<WaitlistModalProps> = ({ onClose }) => {
  const [email, setEmail] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [cadExperience, setCadExperience] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Insert the waitlist data into the Supabase table called 'waitlist'
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { data, error } = await supabase
      .from('waitlist')
      .insert([{ email, job_title: jobTitle, cad_experience: cadExperience }]);

    if (error) {
      console.error('Error adding to waitlist:', error.message);
      setErrorMsg('There was an error submitting your info. Please try again.');
      return;
    }
    
    setSubmitted(true);
  };

  return (
    <div className="waitlist-modal-overlay">
      <div className="waitlist-modal-content">
        <button className="close-button" onClick={onClose}>
          &times;
        </button>

        {!submitted ? (
          <>
            <h2>Join Our Waitlist</h2>
            <form onSubmit={handleSubmit}>
              <input
                type="email"
                placeholder="Your Email"
                className="waitlist-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <input
                type="text"
                placeholder="Your Job Title"
                className="waitlist-input"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />

              <label className="experience-label">CAD Experience</label>
              <select
                className="waitlist-select"
                value={cadExperience}
                onChange={(e) => setCadExperience(e.target.value)}
                required
              >
                <option value="">Select one</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="expert">Expert</option>
              </select>

              <button type="submit" className="waitlist-submit">
                Join Waitlist
              </button>
            </form>
            {errorMsg && <p className="error-message">{errorMsg}</p>}
          </>
        ) : (
          <>
            <h2>Thank You!</h2>
            <p className="waitlist-message">
              We have added you to our waitlist. We'll be in touch soon!
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default WaitlistModal;
