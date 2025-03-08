import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
// import logo from '../../assets/images/logo.png';
import logo from "../../app/assets/logo.png";
import './Header.css';
import { supabase } from '../../supabaseClient';
import { User } from '@supabase/supabase-js';
import PluginStatusIndicator from '../ui/PluginStatusIndicator';
import { checkPluginLoginStatus } from '../../app/api';
import ProfileIcon from '../icons/ProfileIcon';

interface HeaderProps {
  onLoginClick?: () => void;
  onToggleSidebar?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLoginClick, onToggleSidebar }) => {
  const [user, setUser] = useState<User | null>(null);
  const [pluginStatus, setPluginStatus] = useState({
    isLoggedIn: false,
    isActive: false,
    lastSeen: null as number | null
  });
  const [profileMenuOpen, setProfileMenuOpen] = useState(false); // New state for profile menu
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  const location = useLocation();
  // Update this to match all dashboard routes, including those with chat IDs
  const isDashboardPage = location.pathname === '/dashboard' || location.pathname.startsWith('/dashboard/');

  // Monitor window width for responsive adjustments
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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

  // Effect to check plugin login status for authenticated users on dashboard
  useEffect(() => {
    // Only check status if we're on the dashboard and have a user
    if (!isDashboardPage || !user) {
      return;
    }

    const checkStatus = async () => {
      try {
        const result = await checkPluginLoginStatus(user.id);

        if (result.status) {
          // Take is_logged_out into account - if explicitly logged out, override isLoggedIn
          const isPluginLoggedIn = result.is_connected || false;
          const isPluginLoggedOut = result.is_logged_out || false;

          setPluginStatus({
            isLoggedIn: isPluginLoggedIn && !isPluginLoggedOut, // Ensure logged out status is respected
            isActive: result.is_active,
            lastSeen: result.last_seen_timestamp
          });

          console.log(`Plugin status updated: Connected=${isPluginLoggedIn}, LoggedOut=${isPluginLoggedOut}, Active=${result.is_active}`);
        }
      } catch (error) {
        console.error('Error checking plugin status:', error);
      }
    };

    // Initial check
    checkStatus();

    // Set up polling interval (every 2 minutes = 120000ms)
    const intervalId = setInterval(checkStatus, 120000);

    // Clean up interval on unmount
    return () => clearInterval(intervalId);
  }, [user, isDashboardPage]);

  // Function to manually refresh plugin status
  const handleRefreshPluginStatus = async () => {
    if (!user) return;

    try {
      const result = await checkPluginLoginStatus(user.id);

      if (result.status) {
        // Take is_logged_out into account - if explicitly logged out, override isLoggedIn
        const isPluginLoggedIn = result.is_connected || false;
        const isPluginLoggedOut = result.is_logged_out || false;

        setPluginStatus({
          isLoggedIn: isPluginLoggedIn && !isPluginLoggedOut, // Ensure logged out status is respected
          isActive: result.is_active,
          lastSeen: result.last_seen_timestamp
        });

        console.log(`Plugin status manually refreshed: Connected=${isPluginLoggedIn}, LoggedOut=${isPluginLoggedOut}, Active=${result.is_active}`);
      }
    } catch (error) {
      console.error('Error refreshing plugin status:', error);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    window.location.href = '/'; // Redirect to home page
  };

  // Toggle profile menu
  const toggleProfileMenu = () => {
    setProfileMenuOpen(!profileMenuOpen);
  };

  // Determine if we should show the plugin status based on screen width
  const showPluginStatus = windowWidth > 700;

  return (
    <header className="header">
      <div className={`header-container ${isDashboardPage ? 'dashboard-layout' : 'home-layout'}`}>
        {/* Left section - sidebar button and plugin status on dashboard, logo on home */}
        <div className="left-section">
          {isDashboardPage ? (
            <>
              {onToggleSidebar &&
                <button className="menu-btn" onClick={onToggleSidebar}>
                  &#9776;
                </button>
              }

              {/* Plugin status indicator - only shown on dashboard for logged in users */}
              {user && showPluginStatus && (
                <div className="plugin-status-wrapper">
                  <PluginStatusIndicator
                    isLoggedIn={pluginStatus.isLoggedIn}
                    isActive={pluginStatus.isActive}
                    lastSeen={pluginStatus.lastSeen}
                    onRefresh={handleRefreshPluginStatus}
                  />
                </div>
              )}
            </>
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

        {/* User action section */}
        <div className="user-actions">
          {user ? (
            <>
              <button
                className="profile-button"
                onClick={toggleProfileMenu}
              >
                <ProfileIcon size={24} color="#fff" />
              </button>
              {profileMenuOpen && (
                <div className="profile-menu-modal">
                  <div>{user.email}</div>

                  <button
                    className="logout-button"
                    onClick={handleLogout}
                  >
                    Logout
                  </button>
                </div>
              )}
            </>
          ) : (
            onLoginClick && (
              <button className="login-button" onClick={onLoginClick}>
                Login
              </button>
            )
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
