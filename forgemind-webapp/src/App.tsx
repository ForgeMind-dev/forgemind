import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Home from './pages/Home';
import Footer from './components/layout/Footer';
import Dashboard from './pages/Dashboard';
import LoginModal from './components/ui/LoginModal';
import WaitlistModal from './components/ui/WaitlistModal';
import EmbeddedApp from './EmbeddedApp';
import './App.css';

const App: React.FC = () => {
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showWaitlistModal, setShowWaitlistModal] = useState(false);

  const openLoginModal = () => setShowLoginModal(true);
  const closeLoginModal = () => setShowLoginModal(false);
  const openWaitlistModal = () => setShowWaitlistModal(true);
  const closeWaitlistModal = () => setShowWaitlistModal(false);

  const handleOpenWaitlistFromLogin = () => {
    closeLoginModal();
    openWaitlistModal();
  };

  return (
    <>
      <Header onLoginClick={openLoginModal} />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/embedded" element={<EmbeddedApp />} />
        </Routes>
      </main>
      <Footer />
      {showLoginModal && (
        <LoginModal
          onClose={closeLoginModal}
          onOpenWaitlist={handleOpenWaitlistFromLogin}
        />
      )}
      {showWaitlistModal && <WaitlistModal onClose={closeWaitlistModal} />}
    </>
  );
};

export default App;
