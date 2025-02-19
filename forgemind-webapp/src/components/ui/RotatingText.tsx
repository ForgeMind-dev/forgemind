// src/components/ui/RotatingText.tsx
import React, { useState, useEffect } from 'react';
import './RotatingText.css';

interface RotatingTextProps {
  items: string[];
  interval?: number; // time in ms between rotations
}

const RotatingText: React.FC<RotatingTextProps> = ({ items, interval = 2000 }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % items.length);
    }, interval);
    return () => clearInterval(timer);
  }, [items, interval]);

  return (
    <span className="rotating-text">
      {items[currentIndex]}
    </span>
  );
};

export default RotatingText;
