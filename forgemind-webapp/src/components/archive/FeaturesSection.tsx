import React from 'react';
import FeatureCard from './FeatureCard';
import './FeaturesSection.css';

const features = [
  {
    title: 'Seamless CAD Integration',
    description: 'Integrate effortlessly with leading CAD tools like CATIA, SOLIDWORKS, and AutoCAD.',
    icon: '🖥️', // placeholder icon; you can replace this with an SVG or icon component
  },
  {
    title: 'Intelligent AI Assistance',
    description: 'Optimize your design workflows and reduce iteration times with advanced AI.',
    icon: '🤖',
  },
  {
    title: 'Optimized Workflows',
    description: 'Streamline your process from ideation to production with real-time insights.',
    icon: '⚙️',
  },
  {
    title: 'Enterprise-Grade Reliability',
    description: 'Built for scale, ensuring high performance and robust integrations.',
    icon: '🔒',
  },
];

const FeaturesSection = () => {
  return (
    <section className="features-section">
      <h2>Features</h2>
      <div className="features-grid">
        {features.map((feature, index) => (
          <FeatureCard
            key={index}
            title={feature.title}
            description={feature.description}
            icon={<span>{feature.icon}</span>}
          />
        ))}
      </div>
    </section>
  );
};

export default FeaturesSection;
