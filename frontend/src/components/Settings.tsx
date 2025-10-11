import React, { useState, useEffect } from 'react';
import { api, MealScheduleDto, MealScheduleUpdate } from '../api';

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
      // Reload after creating defaults
      const schedules = await api.getMealSchedules();
      setMealSchedules(schedules);
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
      <div style={{ padding: '2rem' }}>
        <h2 style={{ 
          color: '#4A3A2F', 
          fontWeight: 700, 
          fontSize: '1.8rem',
          marginBottom: '2rem' 
        }}>
          Settings
        </h2>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>
          <p>Loading meal schedules...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ 
        color: '#4A3A2F', 
        fontWeight: 700, 
        fontSize: '1.8rem',
        marginBottom: '2rem' 
      }}>
        Settings
      </h2>

      {error && (
        <div style={{
          background: '#fee',
          color: '#c33',
          padding: '1rem',
          borderRadius: '8px',
          marginBottom: '1rem',
          border: '1px solid #fcc'
        }}>
          {error}
        </div>
      )}

      <div style={{
        background: '#fff',
        borderRadius: '16px',
        boxShadow: '0 2px 8px #8ed1fc22',
        border: '1px solid #f0f0f0',
        padding: '2rem'
      }}>
        <h3 style={{ 
          color: '#4A3A2F', 
          fontSize: '1.4rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          🍽️ Meal Schedule
        </h3>
        
        <p style={{ 
          color: '#666', 
          marginBottom: '1.5rem',
          fontSize: '0.9rem'
        }}>
          Set your preferred meal times for breakfast, lunch, and dinner.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {mealSchedules.map((meal) => (
            <div key={meal.id} style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '1rem',
              background: '#f8f9fa',
              borderRadius: '8px',
              border: '1px solid #e9ecef'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: '#28a745',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '1.2rem'
                }}>
                  {meal.meal_name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div style={{ 
                    fontWeight: '600', 
                    color: '#4A3A2F',
                    textTransform: 'capitalize',
                    fontSize: '1.1rem'
                  }}>
                    {meal.meal_name}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                {editingMeal === meal.meal_name ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
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
                      style={{
                        padding: '0.5rem',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '0.9rem'
                      }}
                    />
                    <button
                      onClick={() => handleSave(meal.meal_name)}
                      style={{
                        background: '#28a745',
                        color: 'white',
                        border: 'none',
                        padding: '0.5rem 1rem',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.9rem'
                      }}
                    >
                      Save
                    </button>
                    <button
                      onClick={handleCancel}
                      style={{
                        background: '#6c757d',
                        color: 'white',
                        border: 'none',
                        padding: '0.5rem 1rem',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.9rem'
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ 
                      fontSize: '1.2rem', 
                      fontWeight: '600',
                      color: '#4A3A2F'
                    }}>
                      {formatTime(meal.base_time)}
                    </div>
                    <button
                      onClick={() => handleEdit(meal)}
                      style={{
                        background: '#007bff',
                        color: 'white',
                        border: 'none',
                        padding: '0.5rem 1rem',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.9rem'
                      }}
                    >
                      Edit
                    </button>
                  </div>
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
