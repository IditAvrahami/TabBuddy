import React from 'react';
import FormField from './FormField';
import Option from '../primitives/Option';

interface MealSchedule {
  id: number;
  meal_name: string;
  base_time: string;
}

interface MealDependencyFieldsProps {
  mealSchedules: MealSchedule[];
  mealScheduleId: string;
  mealOffsetMinutes: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
}

const MealDependencyFields: React.FC<MealDependencyFieldsProps> = ({
  mealSchedules,
  mealScheduleId,
  mealOffsetMinutes,
  onChange,
}) => {
  return (
    <>
      <FormField
        label="Meal Schedule"
        type="select"
        name="mealScheduleId"
        value={mealScheduleId}
        onChange={onChange}
        required
      >
        <Option value="">Select meal</Option>
        {mealSchedules.map(meal => (
          <Option key={meal.id} value={meal.id}>
            {meal.meal_name} ({meal.base_time})
          </Option>
        ))}
      </FormField>
      <FormField
        label="Offset (minutes)"
        type="number"
        name="mealOffsetMinutes"
        value={mealOffsetMinutes}
        onChange={onChange}
        placeholder="Negative = before meal, positive = after meal"
        required
      />
    </>
  );
};

export default MealDependencyFields;
