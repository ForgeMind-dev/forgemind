import React from "react";
import fullLogo from "../assets/full_logo.png";

interface HeaderProps {
  onToggleSidebar: () => void;
  chosenCAD: string;
  customCAD: string;
  onConnectClick: () => void;
  onDisconnectClick: () => void;
}

const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  chosenCAD,
  customCAD,
  onConnectClick,
  onDisconnectClick,
}) => {
  // If "Other" is chosen and user typed a custom name, use that; otherwise use chosenCAD
  const cadName = chosenCAD === "Other" && customCAD ? customCAD : chosenCAD;

  return (
    <header className="header-container">
      {/* Sidebar toggle (hamburger) on the left */}
      <button className="menu-btn" onClick={onToggleSidebar}>
        &#9776;
      </button>

      {/* ForgeMind Logo in the center */}
      <div className="header-logo">
        <img src={fullLogo} alt="ForgeMind Logo" />
      </div>

      {/* Connect/Disconnect CAD on the right */}
      <div className="header-right">
        {!chosenCAD ? (
          <button className="connect-cad-btn" onClick={onConnectClick}>
            Connect
          </button>
        ) : (
          <div className="chosen-cad-controls">
            <button className="chosen-cad-btn" onClick={onConnectClick}>
              {cadName}
            </button>
            <button className="disconnect-cad-btn" onClick={onDisconnectClick}>
              Disconnect
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
