import React from 'react';
import { DrugDto } from '../api';

interface DrugListProps {
  drugs: DrugDto[];
  loading: boolean;
  error: string | null;
  onAddDrug: () => void;
  onEditDrug: (drug: DrugDto) => void;
  onDeleteDrug: (drugName: string) => void;
}

const DrugList: React.FC<DrugListProps> = ({ drugs, loading, error, onAddDrug, onEditDrug, onDeleteDrug }) => {
  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '2rem' 
      }}>
        <h2 style={{ 
          color: '#4A3A2F', 
          fontWeight: 700, 
          fontSize: '1.8rem',
          margin: 0 
        }}>
          My Drugs
        </h2>
        <button
          onClick={onAddDrug}
          style={{
            background: '#F6A96B',
            color: '#4A3A2F',
            border: 'none',
            borderRadius: '50%',
            width: '56px',
            height: '56px',
            fontSize: '24px',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: '0 4px 12px #f6a96b33',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'scale(1.1)';
            e.currentTarget.style.boxShadow = '0 6px 16px #f6a96b44';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.boxShadow = '0 4px 12px #f6a96b33';
          }}
        >
          +
        </button>
      </div>

      {error && (
        <div style={{ 
          color: '#b00020', 
          background: '#ffebee',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          border: '1px solid #ffcdd2'
        }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '2rem',
          color: '#4A3A2F',
          fontSize: '1.1rem'
        }}>
          Loading drugs...
        </div>
      ) : drugs.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '3rem',
          color: '#4A3A2F',
          background: '#fff',
          borderRadius: '16px',
          boxShadow: '0 2px 8px #8ed1fc22'
        }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>💊</div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#4A3A2F' }}>No drugs added yet</h3>
          <p style={{ margin: 0, color: '#666' }}>Click the + button to add your first drug</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {drugs.map((drug, idx) => (
            <div 
              key={idx} 
              style={{ 
                background: '#fff', 
                borderRadius: '16px', 
                boxShadow: '0 2px 8px #8ed1fc22', 
                padding: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                transition: 'all 0.2s ease',
                border: '1px solid #f0f0f0'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 16px #8ed1fc33';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 2px 8px #8ed1fc22';
              }}
            >
              <div style={{ 
                display: 'inline-block', 
                width: 48, 
                height: 48, 
                borderRadius: 24, 
                background: drug.kind === 'pill' 
                  ? 'linear-gradient(180deg, #8ED1FC 50%, #F6A96B 50%)' 
                  : 'linear-gradient(180deg, #F6A96B 50%, #8ED1FC 50%)', 
                marginRight: 20, 
                border: '3px solid #8ED1FC', 
                position: 'relative',
                flexShrink: 0
              }}>
                <span style={{ 
                  position: 'absolute', 
                  left: 12, 
                  top: 12, 
                  width: 6, 
                  height: 6, 
                  background: '#4A3A2F', 
                  borderRadius: '50%' 
                }}></span>
                <span style={{ 
                  position: 'absolute', 
                  right: 12, 
                  top: 12, 
                  width: 6, 
                  height: 6, 
                  background: '#4A3A2F', 
                  borderRadius: '50%' 
                }}></span>
                <span style={{ 
                  position: 'absolute', 
                  left: 15, 
                  top: 24, 
                  width: 18, 
                  height: 6, 
                  borderRadius: 3, 
                  background: '#4A3A2F' 
                }}></span>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ 
                  fontWeight: 700, 
                  color: '#4A3A2F', 
                  fontSize: '1.2rem',
                  marginBottom: '0.5rem'
                }}>
                  {drug.name}
                </div>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                  gap: '0.5rem',
                  color: '#4A3A2F', 
                  fontSize: '0.95rem' 
                }}>
                  <div><strong>Type:</strong> {drug.kind.charAt(0).toUpperCase() + drug.kind.slice(1)}</div>
                  <div>
                    <strong>Amount:</strong> {drug.kind === 'pill' 
                      ? `${drug.amount_per_dose} pill(s) per dose` 
                      : `${drug.amount_per_dose} ml per dose`
                    }
                  </div>
                  <div><strong>Duration:</strong> {drug.duration} day(s)</div>
                  <div><strong>Frequency:</strong> {drug.amount_per_day} time(s) per day</div>
                </div>
              </div>
              
              <div style={{ 
                display: 'flex', 
                gap: '0.5rem',
                flexShrink: 0
              }}>
                <button
                  onClick={() => onEditDrug(drug)}
                  style={{
                    background: 'transparent',
                    color: '#4A3A2F',
                    border: '2px solid #8ED1FC',
                    borderRadius: '8px',
                    width: '40px',
                    height: '40px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '16px',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.background = '#8ED1FC';
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                  title="Edit drug"
                >
                  ✏️
                </button>
                <button
                  onClick={() => {
                    if (window.confirm(`Are you sure you want to delete "${drug.name}"?`)) {
                      onDeleteDrug(drug.name);
                    }
                  }}
                  style={{
                    background: 'transparent',
                    color: '#FF6B6B',
                    border: '2px solid #FF6B6B',
                    borderRadius: '8px',
                    width: '40px',
                    height: '40px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '16px',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.background = '#FF6B6B';
                    e.currentTarget.style.color = 'white';
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.color = '#FF6B6B';
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                  title="Delete drug"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DrugList;
