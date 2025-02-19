import React from 'react';
import './About.css';

const About = () => {
  return (
    <section className="about">
      <div className="about-container">
        <h2 className="about-title">Our Vision</h2>
        <p className="about-text">
          At ForgeMind, we envision a future where mechanical design is reimagined. 
          Our goal is to empower creative minds, designers, engineers, and architects, to push the boundaries of innovation 
          and inspire a new era of precision and ingenuity.
        </p>

        <h3 className="team-title">Our Team</h3>
        <div className="team">
          {/* Berat */}
          <div className="team-member">
            <p className="team-name">Berat Celik</p>
            <p className="team-role">CEO</p>
            <div className="team-links">
              <a href="mailto:berat@forgemind.dev" className="icon-link" title="Email Berat">
                <span className="email-icon" />
              </a>
              <a
                href="https://www.linkedin.com/in/beratcelik1/"
                className="icon-link"
                target="_blank"
                rel="noopener noreferrer"
                title="LinkedIn Profile"
              >
                <span className="linkedin-icon" />
              </a>
            </div>
          </div>

          {/* Furkan */}
          <div className="team-member">
            <p className="team-name">Furkan Toprak</p>
            <p className="team-role">CTO</p>
            <div className="team-links">
              <a href="mailto:furkan@forgemind.dev" className="icon-link" title="Email Furkan">
                <span className="email-icon" />
              </a>
              <a
                href="https://www.linkedin.com/in/furkantoprak/"
                className="icon-link"
                target="_blank"
                rel="noopener noreferrer"
                title="LinkedIn Profile"
              >
                <span className="linkedin-icon" />
              </a>
            </div>
          </div>

          {/* Ata */}
          <div className="team-member">
            <p className="team-name">Ata Zavaro</p>
            <p className="team-role">CPO</p>
            <div className="team-links">
              <a href="mailto:ata@forgemind.dev" className="icon-link" title="Email Ata">
                <span className="email-icon" />
              </a>
              <a
                href="https://www.linkedin.com/in/ata-zavaro/"
                className="icon-link"
                target="_blank"
                rel="noopener noreferrer"
                title="LinkedIn Profile"
              >
                <span className="linkedin-icon" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
