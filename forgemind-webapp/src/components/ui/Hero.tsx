import React, { useState } from 'react';
import { motion } from 'framer-motion';
import RotatingText from './RotatingText';
import './Hero.css';
import WaitlistModal from './WaitlistModal'; // Adjust the path if needed

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
  const [showWaitlist, setShowWaitlist] = useState(false);

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
        <motion.p
          className="hero-subtitle"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          Accelerate mechanical design in{' '}
          <span className="rotating-highlight">
            <RotatingText items={cadPlatforms} interval={1500} />
          </span>
        </motion.p>

        {/* Additional text to build curiosity */}
        <motion.p
          className="hero-extra"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          Are you a mechanical designer, architect, or product engineer?<br />
          Join our waitlist to be among the first to experience our breakthrough.
        </motion.p>

        {/* CTA Button */}
        <motion.button
          className="hero-cta"
          onClick={() => setShowWaitlist(true)}
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          Join Waitlist
        </motion.button>
      </div>
      {showWaitlist && <WaitlistModal onClose={() => setShowWaitlist(false)} />}
    </section>
  );
};

export default Hero;
