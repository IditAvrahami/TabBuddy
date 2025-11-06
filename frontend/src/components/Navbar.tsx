import React from 'react';

interface NavbarProps {
  activeTab: 'drugs' | 'settings';
  onTabChange: (tab: 'drugs' | 'settings') => void;
}

const Navbar: React.FC<NavbarProps> = ({ activeTab, onTabChange }) => {
  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '1rem 2rem',
      background: '#FFFCF6',
      borderBottom: '2px solid #8ED1FC',
      borderRadius: '24px 24px 0 0'
    }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <img
          src={process.env.PUBLIC_URL + '/tab-icon.png'}
          alt="TabBuddy logo"
          style={{ width: 48, height: 48, marginRight: 12 }}
        />
        <h1 style={{
          color: '#4A3A2F',
          fontWeight: 800,
          fontSize: '2rem',
          margin: 0,
          letterSpacing: 1
        }}>
          TabBuddy
        </h1>
      </div>

      <div style={{ display: 'flex', gap: '1rem' }}>
        <button
          onClick={() => onTabChange('drugs')}
          style={{
            background: activeTab === 'drugs' ? '#F6A96B' : 'transparent',
            color: '#4A3A2F',
            border: '2px solid #F6A96B',
            borderRadius: '12px',
            padding: '0.75rem 1.5rem',
            fontWeight: 700,
            fontSize: '1rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            boxShadow: activeTab === 'drugs' ? '0 2px 8px #f6a96b33' : 'none'
          }}
        >
          Drugs
        </button>
        <button
          onClick={() => onTabChange('settings')}
          style={{
            background: activeTab === 'settings' ? '#F6A96B' : 'transparent',
            color: '#4A3A2F',
            border: '2px solid #F6A96B',
            borderRadius: '12px',
            padding: '0.75rem 1.5rem',
            fontWeight: 700,
            fontSize: '1rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            boxShadow: activeTab === 'settings' ? '0 2px 8px #f6a96b33' : 'none'
          }}
        >
          Settings
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
