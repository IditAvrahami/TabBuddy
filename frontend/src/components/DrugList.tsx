import React from 'react';
import { DrugDto } from '../api';
import { convertUTCToLocalTime, formatTimeWithTimezone } from '../utils/timezone';
import Icon from './Icon';
import './DrugList.css';

interface DrugListProps {
  drugs: DrugDto[];
  loading: boolean;
  error: string | null;
  onAddDrug: () => void;
  onEditDrug: (drug: DrugDto) => void;
  onDeleteDrug: (drugId: number) => void;
}

const DrugList: React.FC<DrugListProps> = ({ drugs, loading, error, onAddDrug, onEditDrug, onDeleteDrug }) => {
  const getTimingDescription = (drug: DrugDto): string => {
    switch (drug.dependency_type) {
      case 'absolute':
        // Convert UTC time to local time for display
        const localTime = drug.absolute_time ? convertUTCToLocalTime(drug.absolute_time) : '';
        return `At ${localTime} (local time)`;
      case 'meal':
        return `Meal dependency (${drug.meal_timing} meal)`;
      case 'drug':
        return `Depends on another drug`;
      case 'independent':
      default:
        return 'Independent timing';
    }
  };
  return (
    <div className="drug-list-container">
      <div className="drug-list-header">
        <h2 className="drug-list-title">
          My Drugs
        </h2>
        <button
          onClick={onAddDrug}
          className="add-drug-button"
        >
          +
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading-message">
          Loading drugs...
        </div>
      ) : drugs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <Icon name="pill" size={48} />
          </div>
          <h3 className="empty-state-title">No drugs added yet</h3>
          <p className="empty-state-text">Click the + button to add your first drug</p>
        </div>
      ) : (
        <div className="drug-list">
          {drugs.map((drug, idx) => (
            <div
              key={idx}
              className="drug-item"
            >
              <div className={`drug-icon ${drug.kind}`}>
                <span className="drug-icon-dot drug-icon-dot-left"></span>
                <span className="drug-icon-dot drug-icon-dot-right"></span>
                <span className="drug-icon-line"></span>
              </div>
              <div className="drug-info">
                <div className="drug-name">
                  {drug.name}
                </div>
                <div className="drug-details">
                  <div><strong>Type:</strong> {drug.kind.charAt(0).toUpperCase() + drug.kind.slice(1)}</div>
                  <div>
                    <strong>Amount:</strong> {drug.kind === 'pill'
                      ? `${drug.amount_per_dose} pill(s) per dose`
                      : `${drug.amount_per_dose} ml per dose`
                    }
                  </div>
                  <div><strong>Start:</strong> {new Date(drug.start_date).toLocaleDateString()}</div>
                  <div><strong>End:</strong> {drug.end_date ? new Date(drug.end_date).toLocaleDateString() : 'No end date'}</div>
                  <div><strong>Frequency:</strong> {drug.frequency_per_day} time(s) per day</div>
                  <div><strong>Timing:</strong> {getTimingDescription(drug)}</div>
                </div>
              </div>

              <div className="drug-actions">
                <button
                  onClick={() => onEditDrug(drug)}
                  className="action-button edit-button"
                  title="Edit drug"
                >
                  <Icon name="edit" size={20} />
                </button>
                <button
                  onClick={() => {
                    if (window.confirm(`Are you sure you want to delete "${drug.name}"?`)) {
                      onDeleteDrug(drug.id);
                    }
                  }}
                  className="action-button delete-button"
                  title="Delete drug"
                >
                  <Icon name="delete" size={20} />
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
