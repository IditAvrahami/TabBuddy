import React, { useState, useEffect } from 'react';
import { DrugDto, DrugCreateDto, DependencyType, api } from '../api';
import { convertLocalTimeToUTC, convertUTCToLocalTime } from '../utils/timezone';
import Modal from './primitives/Modal';
import Container from './primitives/Container';
import Text from './primitives/Text';
import Form from './primitives/Form';
import Option from './primitives/Option';
import FormField from './forms/FormField';
import DependencySelector from './forms/DependencySelector';
import AbsoluteTimeField from './forms/AbsoluteTimeField';
import MealDependencyFields from './forms/MealDependencyFields';
import DrugDependencyFields from './forms/DrugDependencyFields';
import FormActions from './layout/FormActions';
import Button from './primitives/Button';
import './DrugForm.css';

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
    const loadData = async () => {
      try {
        const [meals, drugs] = await Promise.all([
          api.getMealSchedules(),
          api.listDrugs()
        ]);
        setMealSchedules(meals);
        setExistingDrugs(drugs.filter(d => d.id !== editingDrug?.id));
      } catch (err) {
        console.error('Failed to load dependencies:', err);
      }
    };
    loadData();
  }, [editingDrug?.id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name || !form.amount || !form.startDate) return;
    if (form.dependencyType !== 'absolute' && !form.frequencyPerDay) return;

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
    <Modal visible={true} onClose={onCancel} className="drug-form-modal">
      <Container className="drug-form-header">
        <Text variant="h2" className="drug-form-title">
          {editingDrug ? 'Edit Drug' : 'Add New Drug'}
        </Text>
        <Button
          variant="icon"
          onClick={onCancel}
          className="drug-form-close-button"
        >
          ×
        </Button>
      </Container>

      <Form onSubmit={handleSubmit} className="drug-form">
        <FormField
          label="Drug Name"
          type="text"
          name="name"
          value={form.name}
          onChange={handleChange}
          placeholder="Enter drug name"
          required
        />

        <FormField
          label="Type"
          type="select"
          name="type"
          value={form.type}
          onChange={handleChange}
          required
        >
          <Option value="pill">Pill</Option>
          <Option value="liquid">Liquid</Option>
        </FormField>

        <FormField
          label="Amount per Dose"
          type="number"
          name="amount"
          value={form.amount}
          onChange={handleChange}
          placeholder={form.type === 'pill' ? 'Number of pills per dose' : 'Amount in ml per dose'}
          min={1}
          required
        />

        <FormField
          label="Start Date"
          type="date"
          name="startDate"
          value={form.startDate}
          onChange={handleChange}
          required
        />

        <FormField
          label="End Date (Optional)"
          type="date"
          name="endDate"
          value={form.endDate}
          onChange={handleChange}
        />

        {form.dependencyType !== 'absolute' && (
          <FormField
            label="Frequency per Day"
            type="select"
            name="frequencyPerDay"
            value={form.frequencyPerDay}
            onChange={handleChange}
            required
          >
            <Option value="">Select frequency</Option>
            <Option value="1">1 time per day</Option>
            <Option value="2">2 times per day</Option>
            <Option value="3">3 times per day</Option>
            <Option value="4">4 times per day</Option>
            <Option value="5">5 times per day</Option>
            <Option value="6">6 times per day</Option>
          </FormField>
        )}

        <DependencySelector
          value={form.dependencyType}
          onChange={handleChange}
        />

        {form.dependencyType === 'absolute' && (
          <AbsoluteTimeField
            value={form.absoluteTime}
            onChange={handleChange}
          />
        )}

        {form.dependencyType === 'meal' && (
          <MealDependencyFields
            mealSchedules={mealSchedules}
            mealScheduleId={form.mealScheduleId}
            mealTiming={form.mealTiming}
            mealOffsetMinutes={form.mealOffsetMinutes}
            onChange={handleChange}
          />
        )}

        {form.dependencyType === 'drug' && (
          <DrugDependencyFields
            existingDrugs={existingDrugs}
            dependsOnDrugId={form.dependsOnDrugId}
            drugOffsetMinutes={form.drugOffsetMinutes}
            onChange={handleChange}
          />
        )}

        <FormActions
          onCancel={onCancel}
          submitLabel={editingDrug ? 'Update Drug' : 'Add Drug'}
          loading={loading}
        />
      </Form>
    </Modal>
  );
};

export default DrugForm;
