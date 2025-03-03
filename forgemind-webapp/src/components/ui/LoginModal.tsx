import React, { useState } from 'react';
import { supabase } from '../../supabaseClient'; // Adjust path as needed
import './LoginModal.css';
import { useNavigate } from 'react-router-dom';
import ForgotPasswordModal from './ForgotPasswordModal';

interface LoginModalProps {
  onClose: () => void;
  onOpenWaitlist: () => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ onClose, onOpenWaitlist }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Use Supabase Auth to sign in with email and password
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setMessage("You don't have access yet.");
    } else {
      onClose(); // Close the modal first
      navigate('/dashboard');
    }
  };

  if (showForgotPassword) {
    return (
      <ForgotPasswordModal
        onClose={onClose}
        onBackToLogin={() => setShowForgotPassword(false)}
      />
    );
  }

  return (
    <div className="login-modal-overlay">
      <div className="login-modal-content">
        <button className="close-button" onClick={onClose}>
          &times;
        </button>
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            className="login-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="login-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="login-submit">
            Login
          </button>
          <button
            type="button"
            className="forgot-password-link"
            onClick={() => setShowForgotPassword(true)}
          >
            Forgot Password?
          </button>
        </form>
        {message && (
          <p className="login-message">
            {message}{' '}
            <button
              className="waitlist-link"
              onClick={() => {
                onClose();
                onOpenWaitlist();
              }}
              style={{ cursor: 'pointer' }}
            >
              Join Waitlist
            </button>
          </p>
        )}
      </div>
    </div>
  );
};

export default LoginModal;
