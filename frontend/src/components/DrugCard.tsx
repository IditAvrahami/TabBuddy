import React from 'react';
import { DrugDto } from '../api';
import { convertUTCToLocalTime } from '../utils/timezone';
import Container from './primitives/Container';
import Text from './primitives/Text';
import IconButton from './primitives/IconButton';
import './DrugCard.css';

interface DrugCardProps {
  drug: DrugDto;
  onEdit: (drug: DrugDto) => void;
  onDelete: (drugId: number) => void;
}

const DrugCard: React.FC<DrugCardProps> = ({ drug, onEdit, onDelete }) => {
  const getTimingDescription = (drug: DrugDto): string => {
    switch (drug.dependency_type) {
      case 'absolute':
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

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${drug.name}"?`)) {
      onDelete(drug.id);
    }
  };

  return (
    <Container className="drug-card">
      <Container className={`drug-card-icon ${drug.kind}`}>
        <Text variant="span" className="drug-card-icon-dot drug-card-icon-dot-left"></Text>
        <Text variant="span" className="drug-card-icon-dot drug-card-icon-dot-right"></Text>
        <Text variant="span" className="drug-card-icon-line"></Text>
      </Container>
      <Container className="drug-card-info">
        <Text variant="p" className="drug-card-name">
          {drug.name}
        </Text>
        <Container className="drug-card-details">
          <Container>
            <Text variant="strong">Type:</Text> {drug.kind.charAt(0).toUpperCase() + drug.kind.slice(1)}
          </Container>
          <Container>
            <Text variant="strong">Amount:</Text> {drug.kind === 'pill'
              ? `${drug.amount_per_dose} pill(s) per dose`
              : `${drug.amount_per_dose} ml per dose`
            }
          </Container>
          <Container>
            <Text variant="strong">Start:</Text> {new Date(drug.start_date).toLocaleDateString()}
          </Container>
          <Container>
            <Text variant="strong">End:</Text> {drug.end_date ? new Date(drug.end_date).toLocaleDateString() : 'No end date'}
          </Container>
          <Container>
            <Text variant="strong">Frequency:</Text> {drug.frequency_per_day} time(s) per day
          </Container>
          <Container>
            <Text variant="strong">Timing:</Text> {getTimingDescription(drug)}
          </Container>
        </Container>
      </Container>

      <Container className="drug-card-actions">
        <IconButton
          iconName="edit"
          onClick={() => onEdit(drug)}
          title="Edit drug"
        />
        <IconButton
          iconName="delete"
          variant="danger"
          onClick={handleDelete}
          title="Delete drug"
        />
      </Container>
    </Container>
  );
};

export default DrugCard;
