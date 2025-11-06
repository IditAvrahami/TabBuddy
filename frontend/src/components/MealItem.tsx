import React from 'react';
import Container from './primitives/Container';
import Text from './primitives/Text';
import TimeInput from './primitives/TimeInput';
import Button from './primitives/Button';
import './MealItem.css';

interface MealSchedule {
  id: number;
  meal_name: string;
  base_time: string;
}

interface MealItemProps {
  meal: MealSchedule;
  isEditing: boolean;
  editTime: string;
  onEdit: () => void;
  onSave: () => void;
  onCancel: () => void;
  onTimeChange: (time: string) => void;
}

const MealItem: React.FC<MealItemProps> = ({
  meal,
  isEditing,
  editTime,
  onEdit,
  onSave,
  onCancel,
  onTimeChange,
}) => {
  const formatTime = (timeStr: string) => {
    const [hours, minutes] = timeStr.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  return (
    <Container className="meal-item">
      <Container className="meal-item-left">
        <Container className="meal-item-icon-circle">
          {meal.meal_name.charAt(0).toUpperCase()}
        </Container>
        <Container>
          <Text variant="p" className="meal-item-name">
            {meal.meal_name}
          </Text>
        </Container>
      </Container>

      <Container className="meal-item-right">
        {isEditing ? (
          <Container className="meal-item-edit-group">
            <TimeInput
              value={editTime}
              onChange={(e) => onTimeChange(e.target.value)}
              className="meal-item-time-input"
            />
            <Button
              variant="primary"
              onClick={onSave}
              className="meal-item-button save-button"
            >
              Save
            </Button>
            <Button
              variant="secondary"
              onClick={onCancel}
              className="meal-item-button cancel-button"
            >
              Cancel
            </Button>
          </Container>
        ) : (
          <>
            <Text variant="p" className="meal-item-time">
              {formatTime(meal.base_time)}
            </Text>
            <Button
              variant="primary"
              onClick={onEdit}
              className="meal-item-button edit-button"
            >
              Edit
            </Button>
          </>
        )}
      </Container>
    </Container>
  );
};

export default MealItem;
