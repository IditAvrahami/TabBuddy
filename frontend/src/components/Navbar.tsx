import React from 'react';
import Nav from './primitives/Nav';
import Container from './primitives/Container';
import Text from './primitives/Text';
import Button from './primitives/Button';
import Icon from './Icon';
import './Navbar.css';

interface NavbarProps {
  activeTab: 'drugs' | 'settings';
  onTabChange: (tab: 'drugs' | 'settings') => void;
}

const Navbar: React.FC<NavbarProps> = ({ activeTab, onTabChange }) => {
  return (
    <Nav className="navbar">
      <Container className="navbar-brand">
        <Icon name="tab-icon" size={48} className="navbar-logo" />
        <Text variant="h1" className="navbar-title">
          TabBuddy
        </Text>
      </Container>

      <Container className="navbar-tabs">
        <Button
          onClick={() => onTabChange('drugs')}
          className={`navbar-tab ${activeTab === 'drugs' ? 'active' : ''}`}
        >
          Drugs
        </Button>
        <Button
          onClick={() => onTabChange('settings')}
          className={`navbar-tab ${activeTab === 'settings' ? 'active' : ''}`}
        >
          Settings
        </Button>
      </Container>
    </Nav>
  );
};

export default Navbar;
