import React, { useState } from 'react';
import { DrugDto } from '../api';

interface DrugFormProps {
  onSubmit: (drug: DrugDto) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
  editingDrug?: DrugDto | null;
}

const DrugForm: React.FC<DrugFormProps> = ({ onSubmit, onCancel, loading, editingDrug }) => {
  const [form, setForm] = useState({
    name: editingDrug?.name || '',
    type: (editingDrug?.kind || 'pill') as 'pill' | 'liquid',
    amount: editingDrug?.amount_per_dose?.toString() || '',
    duration: editingDrug?.duration?.toString() || '',
    meal: 'none',
    timesPerDay: editingDrug?.amount_per_day?.toString() || '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.amount || !form.duration || !form.timesPerDay) return;
    
    const payload: DrugDto = {
      name: form.name,
      kind: form.type,
      amount_per_dose: parseInt(form.amount, 10),
      duration: parseInt(form.duration, 10),
      amount_per_day: parseInt(form.timesPerDay, 10),
    };

    try {
      await onSubmit(payload);
      setForm({ name: '', type: 'pill', amount: '', duration: '', meal: 'none', timesPerDay: '' });
    } catch (err) {
      // Error handling is done in parent component
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: '#FFFCF6',
        borderRadius: '24px',
        padding: '2rem',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem'
        }}>
          <h2 style={{ 
            color: '#4A3A2F', 
            fontWeight: 700, 
            fontSize: '1.8rem',
            margin: 0 
          }}>
            {editingDrug ? 'Edit Drug' : 'Add New Drug'}
          </h2>
          <button
            onClick={onCancel}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '24px',
              color: '#4A3A2F',
              cursor: 'pointer',
              padding: '0.5rem',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '1rem'
        }}>
          <div>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 600, 
              color: '#4A3A2F' 
            }}>
              Drug Name *
            </label>
            <input
              type="text"
              name="name"
              placeholder="Enter drug name"
              value={form.name}
              onChange={handleChange}
              required
              style={{ 
                width: '100%',
                borderRadius: '12px', 
                border: '2px solid #8ED1FC', 
                padding: '0.75rem', 
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 600, 
              color: '#4A3A2F' 
            }}>
              Type *
            </label>
            <select 
              name="type" 
              value={form.type} 
              onChange={handleChange} 
              required 
              style={{ 
                width: '100%',
                borderRadius: '12px', 
                border: '2px solid #8ED1FC', 
                padding: '0.75rem', 
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            >
              <option value="pill">Pill</option>
              <option value="liquid">Liquid</option>
            </select>
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 600, 
              color: '#4A3A2F' 
            }}>
              Amount per Dose *
            </label>
            {form.type === 'pill' ? (
              <input
                type="number"
                name="amount"
                placeholder="Number of pills per dose"
                value={form.amount}
                onChange={handleChange}
                min={1}
                required
                style={{ 
                  width: '100%',
                  borderRadius: '12px', 
                  border: '2px solid #8ED1FC', 
                  padding: '0.75rem', 
                  fontSize: '1rem',
                  boxSizing: 'border-box'
                }}
              />
            ) : (
              <input
                type="number"
                name="amount"
                placeholder="Amount in ml per dose"
                value={form.amount}
                onChange={handleChange}
                min={1}
                required
                style={{ 
                  width: '100%',
                  borderRadius: '12px', 
                  border: '2px solid #8ED1FC', 
                  padding: '0.75rem', 
                  fontSize: '1rem',
                  boxSizing: 'border-box'
                }}
              />
            )}
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 600, 
              color: '#4A3A2F' 
            }}>
              Duration (days) *
            </label>
            <input
              type="number"
              name="duration"
              placeholder="Duration in days"
              value={form.duration}
              onChange={handleChange}
              min={1}
              required
              style={{ 
                width: '100%',
                borderRadius: '12px', 
                border: '2px solid #8ED1FC', 
                padding: '0.75rem', 
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 600, 
              color: '#4A3A2F' 
            }}>
              Meal Timing
            </label>
            <select 
              name="meal" 
              value={form.meal} 
              onChange={handleChange} 
              style={{ 
                width: '100%',
                borderRadius: '12px', 
                border: '2px solid #8ED1FC', 
                padding: '0.75rem', 
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            >
              <option value="none">No need after a meal</option>
              <option value="before">Before a meal</option>
              <option value="after">After a meal</option>
            </select>
          </div>

          <div>
            <label style={{ 
              display: 'block', 
              marginBottom: '0.5rem', 
              fontWeight: 600, 
              color: '#4A3A2F' 
            }}>
              Times per Day *
            </label>
            <select
              name="timesPerDay"
              value={form.timesPerDay}
              onChange={handleChange}
              required
              style={{ 
                width: '100%',
                borderRadius: '12px', 
                border: '2px solid #8ED1FC', 
                padding: '0.75rem', 
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            >
              <option value="">Select frequency</option>
              <option value="1">1 time per day</option>
              <option value="2">2 times per day</option>
              <option value="3">3 times per day</option>
              <option value="4">4 times per day</option>
              <option value="5">5 times per day</option>
              <option value="6">6 times per day</option>
            </select>
          </div>

          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            marginTop: '1rem' 
          }}>
            <button 
              type="button"
              onClick={onCancel}
              style={{ 
                flex: 1,
                background: 'transparent', 
                color: '#4A3A2F', 
                border: '2px solid #8ED1FC', 
                borderRadius: '12px', 
                padding: '0.75rem', 
                fontWeight: 700, 
                fontSize: '1rem', 
                cursor: 'pointer' 
              }}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={loading} 
              style={{ 
                flex: 1,
                background: '#F6A96B', 
                color: '#4A3A2F', 
                border: 'none', 
                borderRadius: '12px', 
                padding: '0.75rem', 
                fontWeight: 700, 
                fontSize: '1rem', 
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
                boxShadow: '0 2px 8px #f6a96b33' 
              }}
            >
              {loading ? (editingDrug ? 'Updating...' : 'Adding...') : (editingDrug ? 'Update Drug' : 'Add Drug')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DrugForm;
