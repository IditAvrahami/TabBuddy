import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ReminderModal from '../src/components/ReminderModal';
import { NotificationDto } from '../src/api';

const mockNotification: NotificationDto = {
  schedule_id: 1,
  drug_id: 1,
  drug_name: 'Test Drug',
  kind: 'pill',
  amount_per_dose: 2,
  dependency_type: 'absolute',
  scheduled_time: '2025-10-20T08:30:00Z'
};

describe('ReminderModal', () => {
  const mockOnSnooze = jest.fn();
  const mockOnDismiss = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders notification details correctly', () => {
    render(
      <ReminderModal
        visible={true}
        notification={mockNotification}
        onSnooze={mockOnSnooze}
        onDismiss={mockOnDismiss}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('💊 Time to take your medication')).toBeInTheDocument();
    expect(screen.getByText('Test Drug')).toBeInTheDocument();
    expect(screen.getByText('2 pill(s)')).toBeInTheDocument();
    expect(screen.getByText('8:30 AM')).toBeInTheDocument();
  });

  it('calls onSnooze with correct parameters when snooze button is clicked', () => {
    render(
      <ReminderModal
        visible={true}
        notification={mockNotification}
        onSnooze={mockOnSnooze}
        onDismiss={mockOnDismiss}
        onClose={mockOnClose}
      />
    );

    const snoozeButton = screen.getByText('Snooze');
    fireEvent.click(snoozeButton);

    expect(mockOnSnooze).toHaveBeenCalledWith(1, 10); // default 10 minutes
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('calls onDismiss when dismiss button is clicked', () => {
    render(
      <ReminderModal
        visible={true}
        notification={mockNotification}
        onSnooze={mockOnSnooze}
        onDismiss={mockOnDismiss}
        onClose={mockOnClose}
      />
    );

    const dismissButton = screen.getByText('Dismiss');
    fireEvent.click(dismissButton);

    expect(mockOnDismiss).toHaveBeenCalledWith(1);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('updates snooze time when dropdown changes', () => {
    render(
      <ReminderModal
        visible={true}
        notification={mockNotification}
        onSnooze={mockOnSnooze}
        onDismiss={mockOnDismiss}
        onClose={mockOnClose}
      />
    );

    const select = screen.getByDisplayValue('10 minutes');
    fireEvent.change(select, { target: { value: '30' } });

    const snoozeButton = screen.getByText('Snooze');
    fireEvent.click(snoozeButton);

    expect(mockOnSnooze).toHaveBeenCalledWith(1, 30);
  });

  it('does not render when visible is false', () => {
    render(
      <ReminderModal
        visible={false}
        notification={mockNotification}
        onSnooze={mockOnSnooze}
        onDismiss={mockOnDismiss}
        onClose={mockOnClose}
      />
    );

    expect(screen.queryByText('💊 Time to take your medication')).not.toBeInTheDocument();
  });

  it('does not render when notification is null', () => {
    render(
      <ReminderModal
        visible={true}
        notification={null}
        onSnooze={mockOnSnooze}
        onDismiss={mockOnDismiss}
        onClose={mockOnClose}
      />
    );

    expect(screen.queryByText('💊 Time to take your medication')).not.toBeInTheDocument();
  });
});

