import React from 'react';
import './TeamSection.css';

const teamMembers = [
  {
    name: 'Berat Celik',
    role: 'CEO',
    image: '/assets/images/berat.jpg',
    bio: 'Founder and visionary behind ForgeMind.',
  },
  {
    name: 'Furkan Toprak',
    role: 'CTO',
    image: '/assets/images/furkan.jpg',
    bio: 'Technical mastermind driving AI innovations.',
  },
  {
    name: 'Ata Zavaro',
    role: 'COO',
    image: '/assets/images/ata.jpg',
    bio: 'Operations guru ensuring seamless execution.',
  },
];

const TeamSection = () => {
  return (
    <section className="team-section">
      <h2>Meet the Team</h2>
      <div className="team-grid">
        {teamMembers.map((member, index) => (
          <div key={index} className="team-member">
            <img src={member.image} alt={member.name} />
            <h3>{member.name}</h3>
            <p className="role">{member.role}</p>
            <p className="bio">{member.bio}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default TeamSection;
