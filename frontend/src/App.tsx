import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';
import { api, type DrugDto } from './api';

function App() {
  const [drugs, setDrugs] = useState<DrugDto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    type: 'pill',
    amount: '',
    duration: '',
    meal: 'none',
    timesPerDay: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const loadDrugs = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await api.listDrugs();
      setDrugs(list);
    } catch (err: any) {
      setError(err.message || 'Failed to load drugs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDrugs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.amount || !form.duration || !form.timesPerDay) return;
    const payload: DrugDto = {
      name: form.name,
      kind: form.type as 'pill' | 'liquid',
      amount_per_dose: parseInt(form.amount, 10),
      duration: parseInt(form.duration, 10),
      amount_per_day: parseInt(form.timesPerDay, 10),
    };

    try {
      setLoading(true);
      setError(null);
      await api.addDrug(payload);
      await loadDrugs();
      setForm({ name: '', type: 'pill', amount: '', duration: '', meal: 'none', timesPerDay: '' });
    } catch (err: any) {
      setError(err.message || 'Failed to add drug');
      alert(err.message || 'Failed to add drug');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDrug = async (drugName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${drugName}"?`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await api.deleteDrug(drugName);
      await loadDrugs();
    } catch (err: any) {
      setError(err.message || 'Failed to delete drug');
      alert(err.message || 'Failed to delete drug');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App" style={{ maxWidth: 420, margin: '2rem auto', fontFamily: 'Nunito, Quicksand, sans-serif', background: '#FFFCF6', borderRadius: 24, boxShadow: '0 4px 24px #f6a96b22', padding: '2rem' }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '2rem' }}>
        <img src={process.env.PUBLIC_URL + '/tab-icon.png'} alt="TabBuddy logo" style={{ width: 64, height: 64, marginRight: 16 }} />
        <h1 style={{ color: '#4A3A2F', fontWeight: 800, fontSize: '2.5rem', margin: 0, letterSpacing: 1 }}>TabBuddy</h1>
      </header>
      <h2 style={{ color: '#4A3A2F', fontWeight: 700, marginBottom: '1rem' }}>Add a Drug</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', background: '#fff', borderRadius: 16, padding: '1.5rem', boxShadow: '0 2px 8px #8ed1fc22' }}>
        <input
          type="text"
          name="name"
          placeholder="Drug Name"
          value={form.name}
          onChange={handleChange}
          required
          style={{ borderRadius: 8, border: '1px solid #8ED1FC', padding: '0.5rem', fontSize: '1rem' }}
        />
        <select name="type" value={form.type} onChange={handleChange} required style={{ borderRadius: 8, border: '1px solid #8ED1FC', padding: '0.5rem', fontSize: '1rem' }}>
          <option value="pill">Pill</option>
          <option value="liquid">Liquid</option>
        </select>
        {form.type === 'pill' ? (
          <input
            type="number"
            name="amount"
            placeholder="Amount of pills per dose"
            value={form.amount}
            onChange={handleChange}
            min={1}
            required
            style={{ borderRadius: 8, border: '1px solid #8ED1FC', padding: '0.5rem', fontSize: '1rem' }}
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
            style={{ borderRadius: 8, border: '1px solid #8ED1FC', padding: '0.5rem', fontSize: '1rem' }}
          />
        )}
        <input
          type="text"
          name="duration"
          placeholder="Duration of treatment (e.g. 7 days)"
          value={form.duration}
          onChange={handleChange}
          required
          style={{ borderRadius: 8, border: '1px solid #8ED1FC', padding: '0.5rem', fontSize: '1rem' }}
        />
        <select name="meal" value={form.meal} onChange={handleChange} required style={{ borderRadius: 8, border: '1px solid #8ED1FC', padding: '0.5rem', fontSize: '1rem' }}>
          <option value="none">No need after a meal</option>
          <option value="before">Before a meal</option>
          <option value="after">After a meal</option>
        </select>
        <select
          name="timesPerDay"
          value={form.timesPerDay}
          onChange={handleChange}
          required
          style={{ borderRadius: 8, border: '1px solid #8ED1FC', padding: '0.5rem', fontSize: '1rem' }}
        >
          <option value="">How many times per day?</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
          <option value="5">5</option>
          <option value="6">6</option>
        </select>
        <button type="submit" disabled={loading} style={{ background: '#F6A96B', color: '#4A3A2F', border: 'none', borderRadius: 8, padding: '0.75rem', fontWeight: 700, fontSize: '1.1rem', cursor: 'pointer', boxShadow: '0 2px 8px #f6a96b33' }}>{loading ? 'Adding...' : 'Add Drug'}</button>
      </form>
      {error && <div style={{ color: '#b00020', marginTop: '1rem' }}>{error}</div>}
      <h3 style={{ marginTop: '2rem', color: '#4A3A2F', fontWeight: 700 }}>Drugs List</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {drugs.map((drug, idx) => (
          <li key={idx} style={{ marginBottom: '1rem', background: '#fff', borderRadius: 12, boxShadow: '0 1px 4px #8ed1fc22', padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              <span style={{ display: 'inline-block', width: 32, height: 32, borderRadius: 16, background: drug.kind === 'pill' ? 'linear-gradient(180deg, #8ED1FC 50%, #F6A96B 50%)' : 'linear-gradient(180deg, #F6A96B 50%, #8ED1FC 50%)', marginRight: 16, border: '2px solid #8ED1FC', position: 'relative' }}>
                <span style={{ position: 'absolute', left: 8, top: 8, width: 4, height: 4, background: '#4A3A2F', borderRadius: '50%' }}></span>
                <span style={{ position: 'absolute', right: 8, top: 8, width: 4, height: 4, background: '#4A3A2F', borderRadius: '50%' }}></span>
                <span style={{ position: 'absolute', left: 10, top: 16, width: 12, height: 4, borderRadius: 2, background: '#4A3A2F' }}></span>
              </span>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontWeight: 700, color: '#4A3A2F', fontSize: '1.1rem' }}>{drug.name}</div>
                <div style={{ color: '#4A3A2F', fontSize: '0.95rem' }}>Type: {drug.kind.charAt(0).toUpperCase() + drug.kind.slice(1)}</div>
                <div style={{ color: '#4A3A2F', fontSize: '0.95rem' }}>{drug.kind === 'pill' ? `Amount: ${drug.amount_per_dose} pill(s) per dose` : `Amount: ${drug.amount_per_dose} ml per dose`}</div>
                <div style={{ color: '#4A3A2F', fontSize: '0.95rem' }}>Duration: {drug.duration} day(s)</div>
                <div style={{ color: '#4A3A2F', fontSize: '0.9rem' }}>{drug.amount_per_day} time(s) per day</div>
              </div>
            </div>
            <button
              onClick={() => handleDeleteDrug(drug.name)}
              disabled={loading}
              style={{
                background: 'transparent',
                color: '#333333',
                border: 'none',
                borderRadius: 8,
                padding: '0.6rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.6 : 1,
                transition: 'all 0.2s ease',
                marginLeft: '1rem',
                width: '40px',
                height: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onMouseOver={(e) => {
                if (!loading) {
                  e.currentTarget.style.background = '#f0f0f0';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                }
              }}
              onMouseOut={(e) => {
                if (!loading) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.transform = 'translateY(0)';
                }
              }}
              title="Delete drug"
            >
              {loading ? (
                <span style={{ fontSize: '12px', color: '#333333' }}>...</span>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              )}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
