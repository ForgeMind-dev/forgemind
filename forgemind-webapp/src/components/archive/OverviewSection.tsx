import React from 'react';
import './OverviewSection.css';

const OverviewSection = () => {
  return (
    <section className="overview-section">
      <div className="overview-container">
        <h2 className="overview-title">What is ForgeMind?</h2>
        <p className="overview-text">
          ForgeMind is an AI-driven platform that seamlessly integrates with your favorite CAD tools—SolidWorks, CATIA, Rhino, AutoCAD, and Fusion—helping you design faster and build smarter. 
        </p>
        <p className="overview-text">
          By automating repetitive tasks, providing real-time insights, and optimizing design workflows, ForgeMind empowers engineers to bring products to market in record time. Whether you’re designing simple parts or complex assemblies, ForgeMind’s intelligent copilot ensures you stay ahead of the curve.
        </p>
      </div>
    </section>
  );
};

export default OverviewSection;
