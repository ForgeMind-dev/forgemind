import React, { useState, useEffect } from 'react';
import ChatUI from '../app/AppUI'
import './Dashboard.css';
import { useParams, useNavigate } from 'react-router-dom';

const Dashboard = ({ onToggleSidebar, sidebarOpen }: { onToggleSidebar: () => void; sidebarOpen: boolean; }) => {
  // Extract chatId from URL parameters
  const { chatId } = useParams<{ chatId?: string }>();
  const [initialRender, setInitialRender] = useState(true);
  const navigate = useNavigate();
  
  // Use effect to mark initial render as complete
  useEffect(() => {
    // If we have a specific chat ID, preserve the URL during initialization
    if (initialRender) {
      // Wait for next render to complete to ensure URL stability
      const timer = setTimeout(() => {
        setInitialRender(false);
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [initialRender, chatId]);
  
  return (
    <div className="dashboard">
      {/* You can keep a header or other UI elements here if needed */}
      <ChatUI 
        onToggleSidebar={onToggleSidebar} 
        sidebarOpen={sidebarOpen} 
        initialChatId={chatId} 
      />
    </div>
  );
};

export default Dashboard;
