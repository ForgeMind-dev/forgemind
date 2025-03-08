import React, { useState, useEffect } from 'react';
import './PluginStatusIndicator.css';

interface PluginStatusIndicatorProps {
  isLoggedIn: boolean;
  isActive: boolean;
  lastSeen?: number | null;
  onRefresh?: () => void;
}

/**
 * Component to display the status of the Fusion 360 plugin
 */
const PluginStatusIndicator: React.FC<PluginStatusIndicatorProps> = ({
  isLoggedIn,
  isActive,
  lastSeen,
  onRefresh
}) => {
  const [isSmallScreen, setIsSmallScreen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

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

  // Handle refresh click
  const handleRefreshClick = () => {
    if (onRefresh && !isRefreshing) {
      setIsRefreshing(true);
      onRefresh();
      // Reset refreshing state after animation completes
      setTimeout(() => setIsRefreshing(false), 1000);
    }
  };

  // Modify the getStatusText function to make the text more concise
  const getStatusText = () => {
    if (!isLoggedIn) return 'Plugin Offline';
    if (isActive) return 'Plugin Connected';
    return 'Plugin Inactive';
  };

  const statusText = getStatusText();
  // Simplified class logic - if isLoggedIn is false, it's disconnected regardless of isActive
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
      
      {/* Refresh button */}
      <button 
        className={`plugin-refresh-button ${isRefreshing ? 'refreshing' : ''}`} 
        onClick={handleRefreshClick}
        title="Refresh plugin status"
        aria-label="Refresh plugin status"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M23 4v6h-6"></path>
          <path d="M1 20v-6h6"></path>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"></path>
          <path d="M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>
      </button>
    </div>
  );
};

export default PluginStatusIndicator; 