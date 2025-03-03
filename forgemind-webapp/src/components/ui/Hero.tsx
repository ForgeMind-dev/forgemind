import React, { useState } from 'react';
import { motion } from 'framer-motion';
import RotatingText from './RotatingText';
import './Hero.css';
import WaitlistModal from './WaitlistModal'; // Adjust the path if needed
import { supabase } from '../../supabaseClient';
import { User } from '@supabase/supabase-js';
import { useNavigate } from 'react-router-dom';

const cadPlatforms = [
  'SolidWorks',
  'CATIA',
  'Rhino',
  'AutoCAD',
  'Fusion',
  'Inventor',
  'Creo'
];

const Hero = () => {
  const [user, setUser] = React.useState(undefined as undefined | null | User);
  const navigate = useNavigate();

  React.useEffect(() => {
    const getUser = async () => {
      const { data } = await supabase.auth.getUser();
      setUser(data.user);
    };
    getUser();
  }, []);
  const [showWaitlist, setShowWaitlist] = useState(false);

  const handleDashboardClick = () => {
    const button = document.querySelector<HTMLButtonElement>('.hero-dashboard-btn');
    if (button) {
      button.style.transition = 'transform 0.5s ease';
      button.style.transform = 'translateX(100vw)';
      setTimeout(() => {
        navigate('/dashboard');
      }, 470);
    }
  };

  return (
    <section className="hero">
      <div className="hero-content">
        {/* Animated Main Heading */}
        <motion.h1
          className="hero-title"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <span className="highlight"> Design Faster, Build Smarter</span>
        </motion.h1>

        {/* Subheading with Rotating Text */}
        <motion.div
          className="hero-subtitle-container"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <div className="hero-subtitle">
            <span className="fixed-text">Accelerate mechanical design in</span>
            <div className="rotating-highlight">
              <RotatingText items={cadPlatforms} interval={1500} />
            </div>
          </div>
        </motion.div>

        {/* Conditional rendering based on user state */}
        {user ? (
          <>
            <motion.button
              className="hero-dashboard-btn"
              onClick={handleDashboardClick}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.7 }}
            >
              {"Visit Dashboard"}
            </motion.button>
          </>
        ) : (
          <>
            {/* Additional text to build curiosity */}
            < motion.p
              className="hero-extra"
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
            >
              Are you a mechanical designer, architect, or product engineer?<br />
              Join our waitlist to be among the first to experience our breakthrough.
            </motion.p>
            <motion.button
              className="hero-cta"
              onClick={() => setShowWaitlist(true)}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              Join Waitlist
            </motion.button>
          </>
        )}
      </div>
      {showWaitlist && <WaitlistModal onClose={() => setShowWaitlist(false)} />}
    </section >
  );
};

export default Hero;
