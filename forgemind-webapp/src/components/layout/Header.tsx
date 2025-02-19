import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../../assets/images/logo.png';
import './Header.css';

interface HeaderProps {
  onLoginClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLoginClick }) => {
  return (
    <header className="header">
      <nav className="navigation">
        {/* Left Section: Logo */}
        <div className="logo-section">
          <Link to="/">
            <img src={logo} alt="ForgeMind Logo" className="logo-image" />
          </Link>
        </div>
        {/* Right Section: Login Button */}
        <div className="right-section">
          <button className="login-button" onClick={onLoginClick}>
            Login
          </button>
        </div>
      </nav>
    </header>
  );
};

export default Header;
