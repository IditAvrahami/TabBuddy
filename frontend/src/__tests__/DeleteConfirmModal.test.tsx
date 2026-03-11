import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DeleteConfirmModal from '../components/DeleteConfirmModal';
import { DependentSchedulePreview } from '../api';

const baseDep: DependentSchedulePreview = {
  schedule_id: 10,
  drug_name: 'ChildDrug',
  current_depends_on_name: 'ParentDrug',
  current_offset_minutes: 30,
  new_dependency_type: 'drug',
  new_depends_on_name: 'GrandparentDrug',
  new_offset_minutes: 40,
  new_absolute_time: null,
};

describe('DeleteConfirmModal', () => {
  const mockConfirm = jest.fn();
  const mockCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('does not render when visible is false', () => {
    render(
      <DeleteConfirmModal
        visible={false}
        drugName="TestDrug"
        dependents={[]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    expect(screen.queryByText('Delete TestDrug?')).not.toBeInTheDocument();
  });

  it('renders simple confirmation when no dependents', () => {
    render(
      <DeleteConfirmModal
        visible={true}
        drugName="Aspirin"
        dependents={[]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    expect(screen.getByText('Delete Aspirin?')).toBeInTheDocument();
    expect(screen.getByText('Are you sure you want to delete this medication?')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
    expect(screen.queryByText(/depend on it/)).not.toBeInTheDocument();
  });

  it('renders dependent details when dependents exist', () => {
    render(
      <DeleteConfirmModal
        visible={true}
        drugName="ParentDrug"
        dependents={[baseDep]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    expect(screen.getByText('Delete ParentDrug?')).toBeInTheDocument();
    expect(screen.getByText('Deleting this medication schedule will affect other medications.')).toBeInTheDocument();
    expect(screen.getByText('ChildDrug')).toBeInTheDocument();
    expect(screen.getByText('Delete and update schedule')).toBeInTheDocument();
  });

  it('calls onConfirm when confirm button is clicked', () => {
    render(
      <DeleteConfirmModal
        visible={true}
        drugName="TestDrug"
        dependents={[]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    fireEvent.click(screen.getByText('Delete'));
    expect(mockConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(
      <DeleteConfirmModal
        visible={true}
        drugName="TestDrug"
        dependents={[]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    fireEvent.click(screen.getByText('Cancel'));
    expect(mockCancel).toHaveBeenCalledTimes(1);
  });

  // -- formatNewTiming direction tests --

  it('shows "after" for positive drug offset', () => {
    const dep: DependentSchedulePreview = {
      ...baseDep,
      new_dependency_type: 'drug',
      new_depends_on_name: 'DrugA',
      new_offset_minutes: 40,
    };

    render(
      <DeleteConfirmModal
        visible={true}
        drugName="MiddleDrug"
        dependents={[dep]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    expect(screen.getByText('40 min after DrugA')).toBeInTheDocument();
  });

  it('shows "before" for negative drug offset', () => {
    const dep: DependentSchedulePreview = {
      ...baseDep,
      new_dependency_type: 'drug',
      new_depends_on_name: 'DrugA',
      new_offset_minutes: -5,
    };

    render(
      <DeleteConfirmModal
        visible={true}
        drugName="MiddleDrug"
        dependents={[dep]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    expect(screen.getByText('5 min before DrugA')).toBeInTheDocument();
  });

  it('shows "after" for positive meal offset', () => {
    const dep: DependentSchedulePreview = {
      ...baseDep,
      new_dependency_type: 'meal',
      new_depends_on_name: 'Breakfast',
      new_offset_minutes: 30,
      new_absolute_time: null,
    };

    render(
      <DeleteConfirmModal
        visible={true}
        drugName="MealRoot"
        dependents={[dep]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    expect(screen.getByText('30 min after Breakfast')).toBeInTheDocument();
  });

  it('shows "before" for negative meal offset', () => {
    const dep: DependentSchedulePreview = {
      ...baseDep,
      new_dependency_type: 'meal',
      new_depends_on_name: 'Lunch',
      new_offset_minutes: -10,
      new_absolute_time: null,
    };

    render(
      <DeleteConfirmModal
        visible={true}
        drugName="MealRoot"
        dependents={[dep]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    expect(screen.getByText('10 min before Lunch')).toBeInTheDocument();
  });

  it('shows "Independent schedule" when no dependency info', () => {
    const dep: DependentSchedulePreview = {
      ...baseDep,
      new_dependency_type: 'drug',
      new_depends_on_name: null,
      new_offset_minutes: 0,
      new_absolute_time: null,
    };

    render(
      <DeleteConfirmModal
        visible={true}
        drugName="SomeDrug"
        dependents={[dep]}
        onConfirm={mockConfirm}
        onCancel={mockCancel}
      />
    );

    expect(screen.getByText('Independent schedule')).toBeInTheDocument();
  });
});
