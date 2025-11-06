import React, { useState, useEffect } from 'react';
import { api, MealScheduleDto } from '../api';
import Container from './primitives/Container';
import Text from './primitives/Text';
import Card from './primitives/Card';
import LoadingState from './layout/LoadingState';
import ErrorMessage from './layout/ErrorMessage';
import MealItem from './MealItem';
import Icon from './Icon';
import './Settings.css';

const Settings: React.FC = () => {
  const [mealSchedules, setMealSchedules] = useState<MealScheduleDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingMeal, setEditingMeal] = useState<string | null>(null);
  const [editStates, setEditStates] = useState<{[key: string]: {time: string}}>({});

  const defaultMeals = [
    { meal_name: 'breakfast', base_time: '08:00' },
    { meal_name: 'lunch', base_time: '13:00' },
    { meal_name: 'dinner', base_time: '19:00' }
  ];

  useEffect(() => {
    loadMealSchedules();
  }, []);

  const loadMealSchedules = async () => {
    try {
      setLoading(true);
      const schedules = await api.getMealSchedules();

      const sortedSchedules = schedules.sort((a, b) => {
        const order = ['breakfast', 'lunch', 'dinner'];
        return order.indexOf(a.meal_name) - order.indexOf(b.meal_name);
      });

      setMealSchedules(sortedSchedules);

      if (schedules.length === 0) {
        await createDefaultMeals();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load meal schedules');
    } finally {
      setLoading(false);
    }
  };

  const createDefaultMeals = async () => {
    try {
      for (const meal of defaultMeals) {
        await api.createMealSchedule(meal);
      }
      const schedules = await api.getMealSchedules();

      const sortedSchedules = schedules.sort((a, b) => {
        const order = ['breakfast', 'lunch', 'dinner'];
        return order.indexOf(a.meal_name) - order.indexOf(b.meal_name);
      });

      setMealSchedules(sortedSchedules);
    } catch (err) {
      console.error('Failed to create default meals:', err);
    }
  };

  const handleEdit = (meal: MealScheduleDto) => {
    setEditingMeal(meal.meal_name);
    setEditStates({
      ...editStates,
      [meal.meal_name]: {
        time: meal.base_time
      }
    });
  };

  const handleSave = async (mealName: string) => {
    try {
      const editState = editStates[mealName];
      if (!editState) return;

      await api.updateMealSchedule(mealName, {
        base_time: editState.time
      });
      setEditingMeal(null);
      const newEditStates = { ...editStates };
      delete newEditStates[mealName];
      setEditStates(newEditStates);
      await loadMealSchedules();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update meal schedule');
    }
  };

  const handleCancel = () => {
    setEditingMeal(null);
    if (editingMeal) {
      const newEditStates = { ...editStates };
      delete newEditStates[editingMeal];
      setEditStates(newEditStates);
    }
  };

  const handleTimeChange = (mealName: string, time: string) => {
    setEditStates({
      ...editStates,
      [mealName]: {
        ...editStates[mealName],
        time
      }
    });
  };

  if (loading) {
    return (
      <Container className="settings-container">
        <Text variant="h2" className="settings-title">Settings</Text>
        <LoadingState message="Loading meal schedules..." />
      </Container>
    );
  }

  return (
    <Container className="settings-container">
      <Text variant="h2" className="settings-title">Settings</Text>

      {error && <ErrorMessage message={error} />}

      <Card className="settings-card">
        <Text variant="h3" className="settings-card-title">
          <Icon name="meal" size={24} />
          Meal Schedule
        </Text>

        <Text variant="p" className="settings-card-description">
          Set your preferred meal times for breakfast, lunch, and dinner.
        </Text>

        <Container className="meal-list">
          {mealSchedules.map((meal) => (
            <MealItem
              key={meal.id}
              meal={meal}
              isEditing={editingMeal === meal.meal_name}
              editTime={editStates[meal.meal_name]?.time || meal.base_time}
              onEdit={() => handleEdit(meal)}
              onSave={() => handleSave(meal.meal_name)}
              onCancel={handleCancel}
              onTimeChange={(time) => handleTimeChange(meal.meal_name, time)}
            />
          ))}
        </Container>
      </Card>
    </Container>
  );
};

export default Settings;
