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
  // Update this to match all dashboard routes, including those with chat IDs
  const isDashboardPage = location.pathname === '/dashboard' || location.pathname.startsWith('/dashboard/');
  
  useEffect(() => {
    const checkAuth = async () => {
      const { data } = await supabase.auth.getUser();
      // Only update state if we have data
      if (data) {
        setUser(data.user);
      }
    };
    
    checkAuth();
    
    // Listen for auth changes but don't log each event
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      // Only update for meaningful events, skip INITIAL_SESSION to avoid duplicate refreshes
      if (event !== 'INITIAL_SESSION') {
        setUser(session?.user || null);
      }
    });

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
              <button
                className="logout-button"
                onClick={handleLogout}
              >
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
