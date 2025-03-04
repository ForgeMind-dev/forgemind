import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/layout/Header';
import Home from './pages/Home';
import Footer from './components/layout/Footer';
import Dashboard from './pages/Dashboard';
import LoginModal from './components/ui/LoginModal';
import WaitlistModal from './components/ui/WaitlistModal';
import './App.css';

function App() {
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showWaitlistModal, setShowWaitlistModal] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // Effect to add/remove dashboard-page class based on current route
  useEffect(() => {
    const isDashboard = location.pathname === '/dashboard' || location.pathname.startsWith('/dashboard/');
    
    if (isDashboard) {
      document.documentElement.classList.add('dashboard-page');
      document.body.classList.add('dashboard-page');
    } else {
      document.documentElement.classList.remove('dashboard-page');
      document.body.classList.remove('dashboard-page');
    }
  }, [location.pathname]);

  const openLoginModal = () => setShowLoginModal(true);
  const closeLoginModal = () => setShowLoginModal(false);
  const openWaitlistModal = () => setShowWaitlistModal(true);
  const closeWaitlistModal = () => setShowWaitlistModal(false);
  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <div className="App">
      <Header onLoginClick={openLoginModal} onToggleSidebar={toggleSidebar} />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard onToggleSidebar={toggleSidebar} sidebarOpen={sidebarOpen}/>} />
          <Route path="/dashboard/:chatId" element={<Dashboard onToggleSidebar={toggleSidebar} sidebarOpen={sidebarOpen}/>} />
        </Routes>
      </main>
      <Footer />
      {showLoginModal && (
        <LoginModal
          onClose={closeLoginModal}
          onOpenWaitlist={openWaitlistModal}
        />
      )}
      {showWaitlistModal && <WaitlistModal onClose={closeWaitlistModal} />}
    </div>
  );
}

export default App;
