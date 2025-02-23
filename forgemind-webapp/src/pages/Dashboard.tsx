import React from 'react';
import './Dashboard.css';

const Dashboard: React.FC = () => {
    // Determine the URL based on the environment.
    const isDev = process.env.NODE_ENV === 'development';
    // In development, point to the dev server; in production, use a relative path.
    const reactAppUrl = isDev ? 'http://localhost:3000/embedded' : '/embedded';

    return (
        <div className="dashboard-container">
            <h1>Dashboard</h1>
            <iframe
                title="Embedded React App"
                src={reactAppUrl}
                style={{ width: '100%', height: '80vh', border: 'none' }}
            ></iframe>
        </div>
    );
};

export default Dashboard;
