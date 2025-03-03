import React from 'react';
import { Link } from 'react-router-dom';
// import logo from '../../assets/images/logo.png';
import logo from "../../app/assets/full_logo.png";
import './Header.css';
import { supabase } from '../../supabaseClient';
import { User } from '@supabase/supabase-js';

interface HeaderProps {
  onLoginClick?: () => void;
  onToggleSidebar?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLoginClick, onToggleSidebar }) => {
  const [user, setUser] = React.useState(undefined as undefined | null | User);

  React.useEffect(() => {
    const getUser = async () => {
      const { data } = await supabase.auth.getUser();
      setUser(data.user);
    };
    getUser();
  }, []);

  return (
    <header className="header">
      {/* Menu button, absolutely positioned on the left */}
      <div className="menu-btn-container">
        {onToggleSidebar && <button className="menu-btn" onClick={onToggleSidebar}>
          &#9776;
        </button>}
      </div>
      {/* Left Section: Logo */}
      <div className="navigation">
        <nav>
          <div className="logo-section">
            <Link to="/">
              <img src={logo} alt="ForgeMind Logo" className="logo-image" />
            </Link>
          </div>
        </nav>
      </div>
      {/* Right Section: Login Button */}
      <div className="right-section">
        {onLoginClick && user === null && <button className="login-button" onClick={onLoginClick}>
          Login
        </button>}
      </div>
    </header>
  );
};

export default Header;
