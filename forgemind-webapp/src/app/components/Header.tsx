import React from "react";
import fullLogo from "../assets/full_logo.png";

interface HeaderProps {
  onToggleSidebar: () => void;
  showLogo: boolean;
}

const Header: React.FC<HeaderProps> = ({ onToggleSidebar, showLogo }) => {
  return (
    <header className="header-container">
      {/* Menu button, absolutely positioned on the left */}
      <button className="menu-btn" onClick={onToggleSidebar}>
        &#9776;
      </button>

      {/* Centered logo (by default, because the container uses justify-content: center) */}
      <div className="header-logo">
        {showLogo ? (
          <img src={fullLogo} alt="ForgeMind Logo" />
        ) : (
          <div style={{ height: "40px", width: "40px" }}></div>
        )}
      </div>

      {/* Right side placeholder, absolutely positioned on the right */}
      <div className="header-right"></div>
    </header>
  );
};

export default Header;
