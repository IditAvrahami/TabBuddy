import React, { useState, useEffect } from 'react';
import { api, MealScheduleDto, MealScheduleUpdate } from '../api';
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

      // Sort meals in order: breakfast, lunch, dinner
      const sortedSchedules = schedules.sort((a, b) => {
        const order = ['breakfast', 'lunch', 'dinner'];
        return order.indexOf(a.meal_name) - order.indexOf(b.meal_name);
      });

      setMealSchedules(sortedSchedules);

      // If no meal schedules exist, create default ones
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
      // Reload after creating defaults and apply sorting
      const schedules = await api.getMealSchedules();

      // Sort meals in order: breakfast, lunch, dinner
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
      // Remove the edit state for this meal
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
    // Remove the edit state for the currently editing meal
    if (editingMeal) {
      const newEditStates = { ...editStates };
      delete newEditStates[editingMeal];
      setEditStates(newEditStates);
    }
  };

  const formatTime = (timeStr: string) => {
    const [hours, minutes] = timeStr.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  if (loading) {
    return (
      <div className="settings-container">
        <h2 className="settings-title">
          Settings
        </h2>
        <div className="settings-loading">
          <div className="settings-loading-icon">
            <Icon name="hourglass" size={32} />
          </div>
          <p>Loading meal schedules...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-container">
      <h2 className="settings-title">
        Settings
      </h2>

      {error && (
        <div className="settings-error">
          {error}
        </div>
      )}

      <div className="settings-card">
        <h3 className="settings-card-title">
          <Icon name="meal" size={24} />
          Meal Schedule
        </h3>

        <p className="settings-card-description">
          Set your preferred meal times for breakfast, lunch, and dinner.
        </p>

        <div className="meal-list">
          {mealSchedules.map((meal) => (
            <div key={meal.id} className="meal-item">
              <div className="meal-item-left">
                <div className="meal-icon-circle">
                  {meal.meal_name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="meal-name">
                    {meal.meal_name}
                  </div>
                </div>
              </div>

              <div className="meal-item-right">
                {editingMeal === meal.meal_name ? (
                  <div className="meal-edit-group">
                    <input
                      type="time"
                      value={editStates[meal.meal_name]?.time || meal.base_time}
                      onChange={(e) => setEditStates({
                        ...editStates,
                        [meal.meal_name]: {
                          ...editStates[meal.meal_name],
                          time: e.target.value
                        }
                      })}
                      className="meal-time-input"
                    />
                    <button
                      onClick={() => handleSave(meal.meal_name)}
                      className="meal-button save-button"
                    >
                      Save
                    </button>
                    <button
                      onClick={handleCancel}
                      className="meal-button cancel-button"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="meal-time">
                      {formatTime(meal.base_time)}
                    </div>
                    <button
                      onClick={() => handleEdit(meal)}
                      className="meal-button edit-button"
                    >
                      Edit
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Settings;
