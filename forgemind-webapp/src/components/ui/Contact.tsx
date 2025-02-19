import React from 'react';
import './Contact.css';

const Contact = () => {
  return (
    <section className="contact">
      <div className="contact-container">
        <h2>Contact Us</h2>
        <p>
          For inquiries, please email us at{' '}
          <a
            href="mailto:berat@forgemind.dev"
            className="contact-email-link"
          >
            berat@forgemind.dev
          </a>.
        </p>
        <p className="call-info">
          Want to learn more about our product? 
          Feel free to schedule a call below.
        </p>
        {/* Updated link to Calendly */}
        <a
          href="https://calendly.com/berat-forgemind/30min"
          className="book-call"
          target="_blank"
          rel="noopener noreferrer"
        >
          Book a Call
        </a>
      </div>
    </section>
  );
};

export default Contact;
