import React from 'react';
import './TechShowcase.css';

const TechShowcase = () => {
  return (
    <section className="tech-showcase">
      <h2>Technology Showcase</h2>
      <div className="tech-carousel">
        {/* Replace these with your interactive demo or carousel items */}
        <div className="tech-item">
          <img src="/assets/images/cad-integration-demo.svg" alt="CAD Integration Demo" />
          <p>Seamless integration with CAD software.</p>
        </div>
        <div className="tech-item">
          <img src="/assets/images/ai-assistance-demo.svg" alt="AI Assistance Demo" />
          <p>Intelligent AI optimizing your design workflow.</p>
        </div>
        {/* Add more tech items as needed */}
      </div>
    </section>
  );
};

export default TechShowcase;
