import React from 'react';
import './HowItWorks.css';

const HowItWorksSection = () => {
  return (
    <section className="howitworks-section">
      <div className="hiw-container">
        <h2 className="hiw-title">How It Works</h2>
        <div className="steps">
          <div className="step">
            <h3>1. Connect Your CAD</h3>
            <p>Install the ForgeMind plugin and connect your preferred CAD tool, such as SolidWorks or CATIA.</p>
          </div>
          <div className="step">
            <h3>2. Design with AI Assistance</h3>
            <p>ForgeMind’s AI copilots help automate repetitive tasks, suggest improvements, and provide real-time feedback.</p>
          </div>
          <div className="step">
            <h3>3. Refine & Optimize</h3>
            <p>Quickly iterate on complex geometries, assembly relationships, and manufacturability constraints with minimal manual effort.</p>
          </div>
          <div className="step">
            <h3>4. Export & Collaborate</h3>
            <p>Seamlessly export your final designs, share them with your team, and keep all changes synced in one place.</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
