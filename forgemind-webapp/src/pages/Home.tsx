import React from 'react';
import Hero from '../components/ui/Hero';
import About from '../components/ui/About';
import Contact from '../components/ui/Contact';
import './Home.css';

const Home = () => {
  return (
    <div className="landing">
      {/* Hero has its own styling (full-width, black background) */}
      <Hero />

      {/* About section wrapped in .landing-section for consistent spacing & border */}
      <section className="landing-section">
        <About />
      </section>

      {/* Contact section also wrapped in .landing-section */}
      <section className="landing-section">
        <Contact />
      </section>
    </div>
  );
};

export default Home;
