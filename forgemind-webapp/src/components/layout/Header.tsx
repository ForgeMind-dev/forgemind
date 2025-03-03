import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
// import logo from '../../assets/images/logo.png';
import logo from "../../app/assets/logo.png";
import './Header.css';
import { supabase } from '../../supabaseClient';
import { User } from '@supabase/supabase-js';

interface HeaderProps {
  onLoginClick?: () => void;
  onToggleSidebar?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLoginClick, onToggleSidebar }) => {
  const [user, setUser] = useState<User | null>(null);
  const location = useLocation();
  const isDashboardPage = location.pathname === '/dashboard';
  
  useEffect(() => {
    // Get current user when component mounts
    const getCurrentUser = async () => {
      const { data } = await supabase.auth.getUser();
      console.log('Current auth data:', data);
      setUser(data.user);
    };
    
    getCurrentUser();
    
    // Set up auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('Auth state changed:', event, session);
      setUser(session?.user || null);
    });
    
    // Clean up subscription
    return () => {
      subscription.unsubscribe();
    };
  }, []);
  
  const handleLogout = async () => {
    await supabase.auth.signOut();
    window.location.href = '/'; // Redirect to home page
  };

  return (
    <header className="header">
      <div className={`header-container ${isDashboardPage ? 'dashboard-layout' : 'home-layout'}`}>
        {/* Left section - sidebar button on dashboard, logo on home */}
        <div className="left-section">
          {isDashboardPage ? (
            onToggleSidebar && 
            <button className="menu-btn" onClick={onToggleSidebar}>
              &#9776;
            </button>
          ) : (
            <Link to="/" className="home-logo-container">
              <img src={logo} alt="ForgeMind Logo" className="logo-image" />
            </Link>
          )}
        </div>
        
        {/* Centered logo - only shown on dashboard */}
        {isDashboardPage && (
          <div className="logo-section">
            <Link to="/">
              <img src={logo} alt="ForgeMind Logo" className="logo-image" />
            </Link>
          </div>
        )}
        
        {/* Auth section on the right */}
        <div className="auth-section">
          {user ? (
            <div className="auth-container">
              <div className="user-info">
                <span className="user-email">{user.email}</span>
              </div>
              <button className="logout-button" onClick={handleLogout}>
                Logout
              </button>
            </div>
          ) : (
            onLoginClick && <button className="login-button" onClick={onLoginClick}>
              Login
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
