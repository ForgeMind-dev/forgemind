import React, { useState, useEffect } from 'react';
import './PluginStatusIndicator.css';

interface PluginStatusIndicatorProps {
  isLoggedIn: boolean;
  isActive: boolean;
  lastSeen?: number | null;
}

/**
 * Component to display the status of the Fusion 360 plugin
 */
const PluginStatusIndicator: React.FC<PluginStatusIndicatorProps> = ({
  isLoggedIn,
  isActive,
  lastSeen
}) => {
  const [isSmallScreen, setIsSmallScreen] = useState(false);

  // Check screen size on mount and window resize
  useEffect(() => {
    const checkScreenSize = () => {
      setIsSmallScreen(window.innerWidth <= 768);
    };
    
    // Initial check
    checkScreenSize();
    
    // Add resize listener
    window.addEventListener('resize', checkScreenSize);
    
    // Cleanup
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);
  
  // Format last seen time as relative time (e.g., "5 minutes ago")
  const formatLastSeen = () => {
    if (!lastSeen) return 'Never';
    
    const now = Math.floor(Date.now() / 1000);
    const diff = now - lastSeen;
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  // Modify the getStatusText function to make the text more concise
  const getStatusText = () => {
    // Simpler status text that doesn't change based on screen size
    if (!isLoggedIn) return 'Plugin Offline';
    if (isActive) return 'Plugin Connected';
    return 'Plugin Inactive';
  };

  const statusText = getStatusText();
  const statusClass = isLoggedIn ? (isActive ? 'active' : 'inactive') : 'disconnected';

  return (
    <div className="plugin-status-container">
      <div className={`plugin-status-indicator ${statusClass}`}>
        <div className="status-dot"></div>
        <span className="status-text">{statusText}</span>
      </div>
      
      {isLoggedIn && !isActive && lastSeen && !isSmallScreen && (
        <div className="plugin-last-seen">
          {formatLastSeen()}
        </div>
      )}
    </div>
  );
};

export default PluginStatusIndicator; 