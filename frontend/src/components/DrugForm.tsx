import React, { useState, useEffect } from 'react';
import { DrugDto, DrugCreateDto, DependencyType, api } from '../api';
import { convertLocalTimeToUTC, convertUTCToLocalTime, formatTimeWithTimezone } from '../utils/timezone';

interface DrugFormProps {
  onSubmit: (drug: DrugCreateDto) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
  editingDrug?: DrugDto | null;
}

const DrugForm: React.FC<DrugFormProps> = ({ onSubmit, onCancel, loading, editingDrug }) => {
  const [form, setForm] = useState({
    name: editingDrug?.name || '',
    type: (editingDrug?.kind || 'pill') as 'pill' | 'liquid',
    amount: editingDrug?.amount_per_dose?.toString() || '',
    frequencyPerDay: editingDrug?.frequency_per_day?.toString() || '',
    startDate: editingDrug?.start_date || '',
    endDate: editingDrug?.end_date || '',
    dependencyType: (editingDrug?.dependency_type || 'independent') as DependencyType,
    absoluteTime: editingDrug?.absolute_time ? convertUTCToLocalTime(editingDrug.absolute_time) : '',
    mealScheduleId: editingDrug?.meal_schedule_id?.toString() || '',
    mealOffsetMinutes: editingDrug?.meal_offset_minutes?.toString() || '',
    mealTiming: editingDrug?.meal_timing || 'before',
    dependsOnDrugId: editingDrug?.depends_on_drug_id?.toString() || '',
    drugOffsetMinutes: editingDrug?.drug_offset_minutes?.toString() || '',
  });

  const [mealSchedules, setMealSchedules] = useState<any[]>([]);
  const [existingDrugs, setExistingDrugs] = useState<DrugDto[]>([]);

  useEffect(() => {
    // Load meal schedules and existing drugs for dependencies
    const loadData = async () => {
      try {
        const [meals, drugs] = await Promise.all([
          api.getMealSchedules(),
          api.listDrugs()
        ]);
        setMealSchedules(meals);
        setExistingDrugs(drugs.filter(d => d.id !== editingDrug?.id)); // Exclude current drug if editing
      } catch (err) {
        console.error('Failed to load dependencies:', err);
      }
    };
    loadData();
  }, [editingDrug?.id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Timezone conversion now handled by utility functions

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.amount || !form.startDate) return;
    if (form.dependencyType !== 'absolute' && !form.frequencyPerDay) return;

    // Debug timezone conversion
    const convertedTime = form.absoluteTime ? convertLocalTimeToUTC(form.absoluteTime) : undefined;
    console.log('🔧 Timezone Debug:');
    console.log('  Local time from form:', form.absoluteTime);
    console.log('  Converted UTC time:', convertedTime);
    console.log('  Timezone offset:', new Date().getTimezoneOffset(), 'minutes');

    const payload: DrugCreateDto = {
      name: form.name,
      kind: form.type,
      amount_per_dose: parseInt(form.amount, 10),
      frequency_per_day: form.dependencyType === 'absolute' ? 1 : parseInt(form.frequencyPerDay, 10),
      start_date: form.startDate,
      end_date: form.endDate || undefined,
      dependency_type: form.dependencyType,
      // Convert local time to UTC before sending to backend
      absolute_time: convertedTime,
      meal_schedule_id: form.mealScheduleId ? parseInt(form.mealScheduleId, 10) : undefined,
      meal_offset_minutes: form.mealOffsetMinutes ? parseInt(form.mealOffsetMinutes, 10) : undefined,
      meal_timing: form.mealTiming as 'before' | 'after',
      depends_on_drug_id: form.dependsOnDrugId ? parseInt(form.dependsOnDrugId, 10) : undefined,
      drug_offset_minutes: form.drugOffsetMinutes ? parseInt(form.drugOffsetMinutes, 10) : undefined,
    };

    console.log('📤 Payload being sent:', payload);

    try {
      await onSubmit(payload);
      // Reset form
      setForm({
        name: '', type: 'pill', amount: '', frequencyPerDay: '', startDate: '', endDate: '',
        dependencyType: 'independent', absoluteTime: '', mealScheduleId: '', mealOffsetMinutes: '',
        mealTiming: 'before', dependsOnDrugId: '', drugOffsetMinutes: ''
      });
    } catch (err) {
      // Error handling is done in parent component
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: '#FFFCF6',
        borderRadius: '24px',
        padding: '2rem',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem'
        }}>
          <h2 style={{
            color: '#4A3A2F',
            fontWeight: 700,
            fontSize: '1.8rem',
            margin: 0
          }}>
            {editingDrug ? 'Edit Drug' : 'Add New Drug'}
          </h2>
          <button
            onClick={onCancel}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '24px',
              color: '#4A3A2F',
              cursor: 'pointer',
              padding: '0.5rem',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: 600,
              color: '#4A3A2F'
            }}>
              Drug Name *
            </label>
            <input
              type="text"
              name="name"
              placeholder="Enter drug name"
              value={form.name}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                borderRadius: '12px',
                border: '2px solid #8ED1FC',
                padding: '0.75rem',
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: 600,
              color: '#4A3A2F'
            }}>
              Type *
            </label>
            <select
              name="type"
              value={form.type}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                borderRadius: '12px',
                border: '2px solid #8ED1FC',
                padding: '0.75rem',
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            >
              <option value="pill">Pill</option>
              <option value="liquid">Liquid</option>
            </select>
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: 600,
              color: '#4A3A2F'
            }}>
              Amount per Dose *
            </label>
            {form.type === 'pill' ? (
              <input
                type="number"
                name="amount"
                placeholder="Number of pills per dose"
                value={form.amount}
                onChange={handleChange}
                min={1}
                required
                style={{
                  width: '100%',
                  borderRadius: '12px',
                  border: '2px solid #8ED1FC',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  boxSizing: 'border-box'
                }}
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
                style={{
                  width: '100%',
                  borderRadius: '12px',
                  border: '2px solid #8ED1FC',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  boxSizing: 'border-box'
                }}
              />
            )}
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: 600,
              color: '#4A3A2F'
            }}>
              Start Date *
            </label>
            <input
              type="date"
              name="startDate"
              value={form.startDate}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                borderRadius: '12px',
                border: '2px solid #8ED1FC',
                padding: '0.75rem',
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: 600,
              color: '#4A3A2F'
            }}>
              End Date (Optional)
            </label>
            <input
              type="date"
              name="endDate"
              value={form.endDate}
              onChange={handleChange}
              style={{
                width: '100%',
                borderRadius: '12px',
                border: '2px solid #8ED1FC',
                padding: '0.75rem',
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            />
          </div>

          {form.dependencyType !== 'absolute' && (
            <div>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: 600,
                color: '#4A3A2F'
              }}>
                Frequency per Day *
              </label>
              <select
                name="frequencyPerDay"
                value={form.frequencyPerDay}
                onChange={handleChange}
                required
                style={{
                  width: '100%',
                  borderRadius: '12px',
                  border: '2px solid #8ED1FC',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  boxSizing: 'border-box'
                }}
              >
                <option value="">Select frequency</option>
                <option value="1">1 time per day</option>
                <option value="2">2 times per day</option>
                <option value="3">3 times per day</option>
                <option value="4">4 times per day</option>
                <option value="5">5 times per day</option>
                <option value="6">6 times per day</option>
              </select>
            </div>
          )}

          {/* Duration removed: derived from start and end dates */}

          <div>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: 600,
              color: '#4A3A2F'
            }}>
              Timing Dependency *
            </label>
            <select
              name="dependencyType"
              value={form.dependencyType}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                borderRadius: '12px',
                border: '2px solid #8ED1FC',
                padding: '0.75rem',
                fontSize: '1rem',
                boxSizing: 'border-box'
              }}
            >
              <option value="independent">Independent (no dependency)</option>
              <option value="absolute">Absolute time</option>
              <option value="meal">Depends on meal</option>
              <option value="drug">Depends on another drug</option>
            </select>
          </div>

          {/* Absolute Time Dependency */}
          {form.dependencyType === 'absolute' && (
            <div>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: 600,
                color: '#4A3A2F'
              }}>
                Time of Day * (Local Time)
              </label>
              <input
                type="time"
                name="absoluteTime"
                value={form.absoluteTime}
                onChange={handleChange}
                required
                style={{
                  width: '100%',
                  borderRadius: '12px',
                  border: '2px solid #8ED1FC',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  boxSizing: 'border-box'
                }}
              />
              {form.absoluteTime && (
                <div style={{
                  marginTop: '0.5rem',
                  fontSize: '0.9rem',
                  color: '#666',
                  fontStyle: 'italic'
                }}>
                  Will be stored as: {formatTimeWithTimezone(convertLocalTimeToUTC(form.absoluteTime), true)}
                </div>
              )}
            </div>
          )}

          {/* Meal Dependency */}
          {form.dependencyType === 'meal' && (
            <>
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontWeight: 600,
                  color: '#4A3A2F'
                }}>
                  Meal Schedule *
                </label>
                <select
                  name="mealScheduleId"
                  value={form.mealScheduleId}
                  onChange={handleChange}
                  required
                  style={{
                    width: '100%',
                    borderRadius: '12px',
                    border: '2px solid #8ED1FC',
                    padding: '0.75rem',
                    fontSize: '1rem',
                    boxSizing: 'border-box'
                  }}
                >
                  <option value="">Select meal</option>
                  {mealSchedules.map(meal => (
                    <option key={meal.id} value={meal.id}>
                      {meal.meal_name} ({meal.base_time})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontWeight: 600,
                  color: '#4A3A2F'
                }}>
                  Timing *
                </label>
                <select
                  name="mealTiming"
                  value={form.mealTiming}
                  onChange={handleChange}
                  required
                  style={{
                    width: '100%',
                    borderRadius: '12px',
                    border: '2px solid #8ED1FC',
                    padding: '0.75rem',
                    fontSize: '1rem',
                    boxSizing: 'border-box'
                  }}
                >
                  <option value="before">Before meal</option>
                  <option value="after">After meal</option>
                </select>
              </div>
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontWeight: 600,
                  color: '#4A3A2F'
                }}>
                  Offset (minutes) *
                </label>
                <input
                  type="number"
                  name="mealOffsetMinutes"
                  placeholder="Minutes before/after meal"
                  value={form.mealOffsetMinutes}
                  onChange={handleChange}
                  required
                  min={0}
                  style={{
                    width: '100%',
                    borderRadius: '12px',
                    border: '2px solid #8ED1FC',
                    padding: '0.75rem',
                    fontSize: '1rem',
                    boxSizing: 'border-box'
                  }}
                />
              </div>
            </>
          )}

          {/* Drug Dependency */}
          {form.dependencyType === 'drug' && (
            <>
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontWeight: 600,
                  color: '#4A3A2F'
                }}>
                  Depends on Drug *
                </label>
                <select
                  name="dependsOnDrugId"
                  value={form.dependsOnDrugId}
                  onChange={handleChange}
                  required
                  style={{
                    width: '100%',
                    borderRadius: '12px',
                    border: '2px solid #8ED1FC',
                    padding: '0.75rem',
                    fontSize: '1rem',
                    boxSizing: 'border-box'
                  }}
                >
                  <option value="">Select drug</option>
                  {existingDrugs.map(drug => (
                    <option key={drug.id} value={drug.id}>
                      {drug.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontWeight: 600,
                  color: '#4A3A2F'
                }}>
                  Offset (minutes) *
                </label>
                <input
                  type="number"
                  name="drugOffsetMinutes"
                  placeholder="Minutes after dependent drug"
                  value={form.drugOffsetMinutes}
                  onChange={handleChange}
                  required
                  style={{
                    width: '100%',
                    borderRadius: '12px',
                    border: '2px solid #8ED1FC',
                    padding: '0.75rem',
                    fontSize: '1rem',
                    boxSizing: 'border-box'
                  }}
                />
              </div>
            </>
          )}

          <div style={{
            display: 'flex',
            gap: '1rem',
            marginTop: '1rem'
          }}>
            <button
              type="button"
              onClick={onCancel}
              style={{
                flex: 1,
                background: 'transparent',
                color: '#4A3A2F',
                border: '2px solid #8ED1FC',
                borderRadius: '12px',
                padding: '0.75rem',
                fontWeight: 700,
                fontSize: '1rem',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                flex: 1,
                background: '#F6A96B',
                color: '#4A3A2F',
                border: 'none',
                borderRadius: '12px',
                padding: '0.75rem',
                fontWeight: 700,
                fontSize: '1rem',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
                boxShadow: '0 2px 8px #f6a96b33'
              }}
            >
              {loading ? (editingDrug ? 'Updating...' : 'Adding...') : (editingDrug ? 'Update Drug' : 'Add Drug')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DrugForm;
