import React from 'react';
import { DrugDto } from '../api';
import Container from './primitives/Container';
import PageHeader from './layout/PageHeader';
import EmptyState from './layout/EmptyState';
import LoadingState from './layout/LoadingState';
import ErrorMessage from './layout/ErrorMessage';
import DrugCard from './DrugCard';
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
  return (
    <Container className="drug-list-container">
      <PageHeader
        title="My Drugs"
        actionButton={{
          label: '+',
          onClick: onAddDrug,
        }}
      />

      {error && <ErrorMessage message={error} />}

      {loading ? (
        <LoadingState message="Loading drugs..." />
      ) : drugs.length === 0 ? (
        <EmptyState
          icon="pill"
          title="No drugs added yet"
          message="Click the + button to add your first drug"
        />
      ) : (
        <Container className="drug-list">
          {drugs.map((drug, idx) => (
            <DrugCard
              key={idx}
              drug={drug}
              onEdit={onEditDrug}
              onDelete={onDeleteDrug}
            />
          ))}
        </Container>
      )}
    </Container>
  );
};

export default DrugList;
