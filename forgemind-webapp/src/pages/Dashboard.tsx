// forgemind-webapp/src/pages/Dashboard.tsx

import React from 'react';
import ChatUI from '../app/AppUI'
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      {/* You can keep a header or other UI elements here if needed */}
      <ChatUI />
    </div>
  );
};

export default Dashboard;
