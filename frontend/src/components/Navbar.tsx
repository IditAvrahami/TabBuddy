import React from 'react';
import Icon from './Icon';
import './Navbar.css';

interface NavbarProps {
  activeTab: 'drugs' | 'settings';
  onTabChange: (tab: 'drugs' | 'settings') => void;
}

const Navbar: React.FC<NavbarProps> = ({ activeTab, onTabChange }) => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Icon name="tab-icon" size={48} className="navbar-logo" />
        <h1 className="navbar-title">
          TabBuddy
        </h1>
      </div>

      <div className="navbar-tabs">
        <button
          onClick={() => onTabChange('drugs')}
          className={`navbar-tab ${activeTab === 'drugs' ? 'active' : ''}`}
        >
          Drugs
        </button>
        <button
          onClick={() => onTabChange('settings')}
          className={`navbar-tab ${activeTab === 'settings' ? 'active' : ''}`}
        >
          Settings
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
