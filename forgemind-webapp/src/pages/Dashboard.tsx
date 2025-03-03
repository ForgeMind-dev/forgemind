import React from 'react';
import ChatUI from '../app/AppUI'
import './Dashboard.css';

const Dashboard = ({ onToggleSidebar, sidebarOpen }: { onToggleSidebar: () => void; sidebarOpen: boolean; }) => {
  return (
    <div className="dashboard">
      {/* You can keep a header or other UI elements here if needed */}
      <ChatUI onToggleSidebar={onToggleSidebar} sidebarOpen={sidebarOpen} />
    </div>
  );
};

export default Dashboard;
