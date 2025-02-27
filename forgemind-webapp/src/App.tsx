import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
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

  const openLoginModal = () => setShowLoginModal(true);
  const closeLoginModal = () => setShowLoginModal(false);
  const openWaitlistModal = () => setShowWaitlistModal(true);
  const closeWaitlistModal = () => setShowWaitlistModal(false);

  return (
    <div className="App">
      <Header onLoginClick={openLoginModal} />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
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
