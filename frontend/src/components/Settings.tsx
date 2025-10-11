import React from 'react';

const Settings: React.FC = () => {
  return (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ 
        color: '#4A3A2F', 
        fontWeight: 700, 
        fontSize: '1.8rem',
        marginBottom: '2rem' 
      }}>
        Settings
      </h2>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '300px',
        background: '#fff',
        borderRadius: '16px',
        boxShadow: '0 2px 8px #8ed1fc22',
        border: '1px solid #f0f0f0'
      }}>
        <div style={{ textAlign: 'center', color: '#666' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚙️</div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#4A3A2F' }}>Settings Coming Soon</h3>
          <p style={{ margin: 0 }}>This section will be available in a future update</p>
        </div>
      </div>
    </div>
  );
};

export default Settings;
