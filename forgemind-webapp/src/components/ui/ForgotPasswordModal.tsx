import React, { useState } from 'react';
import { supabase } from '../../supabaseClient';
import './ForgotPasswordModal.css';

interface ForgotPasswordModalProps {
  onClose: () => void;
  onBackToLogin: () => void;
}

const ForgotPasswordModal: React.FC<ForgotPasswordModalProps> = ({ onClose, onBackToLogin }) => {
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [step, setStep] = useState<'email' | 'otp' | 'newPassword'>('email');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email);
      
      if (error) throw error;
      
      setMessage('Verification code has been sent to your email.');
      setStep('otp');
    } catch (err: any) {
      setError(err.message || 'Failed to send verification code');
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Verify the OTP using Supabase's verifyOTP method
      const { error } = await supabase.auth.verifyOtp({
        email,
        token: otp,
        type: 'recovery'
      });

      if (error) throw error;
      
      setStep('newPassword');
      setMessage('');
    } catch (err: any) {
      setError(err.message || 'Invalid verification code');
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword
      });

      if (error) throw error;

      setMessage('Password has been reset successfully!');
      setTimeout(() => {
        onBackToLogin();
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to reset password');
    }
  };

  return (
    <div className="forgot-password-modal-overlay">
      <div className="forgot-password-modal-content">
        <button className="close-button" onClick={onClose}>
          &times;
        </button>
        <h2>Reset Password</h2>
        
        {step === 'email' && (
          <form onSubmit={handleSendOTP}>
            <input
              type="email"
              placeholder="Enter your email"
              className="forgot-password-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit" className="forgot-password-submit">
              Send Verification Code
            </button>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={handleVerifyOTP}>
            <p className="otp-instruction">
              Enter the 6-digit verification code sent to your email
            </p>
            <input
              type="text"
              placeholder="Enter verification code"
              className="forgot-password-input otp-input"
              value={otp}
              onChange={(e) => {
                const value = e.target.value.replace(/[^0-9]/g, '');
                if (value.length <= 6) setOtp(value);
              }}
              maxLength={6}
              pattern="[0-9]*"
              inputMode="numeric"
              autoComplete="one-time-code"
              required
            />
            <button type="submit" className="forgot-password-submit">
              Verify Code
            </button>
          </form>
        )}

        {step === 'newPassword' && (
          <form onSubmit={handleResetPassword}>
            <input
              type="password"
              placeholder="Enter new password"
              className="forgot-password-input"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={8}
            />
            <p className="password-requirements">
              Password must be at least 8 characters long
            </p>
            <button type="submit" className="forgot-password-submit">
              Reset Password
            </button>
          </form>
        )}

        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}
        
        <button
          className="back-to-login"
          onClick={onBackToLogin}
        >
          Back to Login
        </button>
      </div>
    </div>
  );
};

export default ForgotPasswordModal; 