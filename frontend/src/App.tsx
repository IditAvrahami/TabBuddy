import React, { useEffect, useState } from 'react';
import './App.css';
import { api, type DrugDto } from './api';
import Navbar from './components/Navbar';
import DrugList from './components/DrugList';
import DrugForm from './components/DrugForm';
import Settings from './components/Settings';

function App() {
  const [activeTab, setActiveTab] = useState<'drugs' | 'settings'>('drugs');
  const [showDrugForm, setShowDrugForm] = useState(false);
  const [editingDrug, setEditingDrug] = useState<DrugDto | null>(null);
  const [drugs, setDrugs] = useState<DrugDto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleAddDrug = async (drug: DrugDto) => {
    try {
      setLoading(true);
      setError(null);
      await api.addDrug(drug);
      await loadDrugs();
      setShowDrugForm(false);
      setEditingDrug(null);
    } catch (err: any) {
      setError(err.message || 'Failed to add drug');
      throw err; // Re-throw to let DrugForm handle the error display
    } finally {
      setLoading(false);
    }
  };

  const handleEditDrug = async (drug: DrugDto) => {
    try {
      setLoading(true);
      setError(null);
      // Use the original drug name as identifier, not the potentially modified name
      await api.updateDrug(editingDrug!.name, drug);
      await loadDrugs();
      setShowDrugForm(false);
      setEditingDrug(null);
    } catch (err: any) {
      setError(err.message || 'Failed to update drug');
      throw err; // Re-throw to let DrugForm handle the error display
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDrug = async (drugName: string) => {
    try {
      setLoading(true);
      setError(null);
      await api.deleteDrug(drugName);
      await loadDrugs();
    } catch (err: any) {
      setError(err.message || 'Failed to delete drug');
    } finally {
      setLoading(false);
    }
  };

  const openEditForm = (drug: DrugDto) => {
    setEditingDrug(drug);
    setShowDrugForm(true);
  };

  const openAddForm = () => {
    setEditingDrug(null);
    setShowDrugForm(true);
  };

  const closeForm = () => {
    setShowDrugForm(false);
    setEditingDrug(null);
  };

  return (
    <div className="App" style={{ 
      maxWidth: 800, 
      margin: '2rem auto', 
      fontFamily: 'Nunito, Quicksand, sans-serif', 
      background: '#FFFCF6', 
      borderRadius: 24, 
      boxShadow: '0 4px 24px #f6a96b22',
      overflow: 'hidden'
    }}>
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      
      {activeTab === 'drugs' ? (
        <DrugList 
          drugs={drugs}
          loading={loading}
          error={error}
          onAddDrug={openAddForm}
          onEditDrug={openEditForm}
          onDeleteDrug={handleDeleteDrug}
        />
      ) : (
        <Settings />
      )}

      {showDrugForm && (
        <DrugForm
          onSubmit={editingDrug ? handleEditDrug : handleAddDrug}
          onCancel={closeForm}
          loading={loading}
          editingDrug={editingDrug}
        />
      )}
    </div>
  );
}

export default App;
