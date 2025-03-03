// src/components/ui/RotatingText.tsx
import React, { useState, useEffect } from 'react';
import './RotatingText.css';

interface RotatingTextProps {
  items: string[];
  interval?: number; // time in ms between rotations
}

const RotatingText: React.FC<RotatingTextProps> = ({ items, interval = 2000 }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [rotate, setRotate] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setRotate(false);
      setTimeout(() => {
        setCurrentIndex((prevIndex) => (prevIndex + 1) % items.length);
        setRotate(true);
      }, 500); // duration of the rotate-out animation
    }, interval);
    return () => clearInterval(timer);
  }, [items, interval]);

  return (
    <span className={`rotating-text ${rotate ? 'rotate-in' : 'rotate-out'}`}>
      {items[currentIndex]}
    </span>
  );
};

export default RotatingText;
