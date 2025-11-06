import React, { useState } from 'react';
import { NotificationDto } from '../api';
import Icon from './Icon';
import './ReminderModal.css';

interface ReminderModalProps {
  visible: boolean;
  notification: NotificationDto | null;
  onSnooze: (scheduleId: number, minutes: number) => void;
  onDismiss: (scheduleId: number) => void;
  onClose: () => void;
}

const ReminderModal: React.FC<ReminderModalProps> = ({
  visible,
  notification,
  onSnooze,
  onDismiss,
  onClose,
}) => {
  const [snoozeMinutes, setSnoozeMinutes] = useState(10);
  const [isProcessing, setIsProcessing] = useState(false);

  if (!visible || !notification) {
    return null;
  }

  const handleSnooze = async () => {
    if (isProcessing || !notification) return;

    setIsProcessing(true);
    try {
      await onSnooze(notification.schedule_id, snoozeMinutes);
      // Modal will be closed by the handler in App.tsx
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDismiss = async () => {
    if (isProcessing || !notification) return;

    setIsProcessing(true);
    try {
      await onDismiss(notification.schedule_id);
      // Modal will be closed by the handler in App.tsx
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="reminder-modal-overlay">
      <div className="reminder-modal-container">
        <div className="reminder-modal-header">
          <h2 className="reminder-modal-title">
            <Icon name="pill" size={24} />
            Time to take your medication
          </h2>
          <p className="reminder-modal-time">
            {formatTime(notification.scheduled_time)}
          </p>
        </div>

        <div className="reminder-modal-drug-info">
          <div className="reminder-modal-drug-name">
            <strong>{notification.drug_name}</strong>
          </div>
          <div className="reminder-modal-drug-details">
            {notification.amount_per_dose} {notification.kind === 'pill' ? 'pill(s)' : 'ml'}
            {notification.dependency_type === 'absolute' && ' at scheduled time'}
          </div>
        </div>

        <div className="reminder-modal-snooze-group">
          <label className="reminder-modal-snooze-label">
            Snooze for:
          </label>
          <select
            value={snoozeMinutes}
            onChange={(e) => setSnoozeMinutes(Number(e.target.value))}
            className="reminder-modal-snooze-select"
          >
            <option value={5}>5 minutes</option>
            <option value={10}>10 minutes</option>
            <option value={15}>15 minutes</option>
            <option value={30}>30 minutes</option>
            <option value={60}>1 hour</option>
          </select>
        </div>

        <div className="reminder-modal-actions">
          <button
            onClick={handleSnooze}
            disabled={isProcessing}
            className="reminder-modal-button snooze-button"
          >
            {isProcessing ? 'Processing...' : 'Snooze'}
          </button>
          <button
            onClick={handleDismiss}
            disabled={isProcessing}
            className="reminder-modal-button dismiss-button"
          >
            {isProcessing ? 'Processing...' : 'Dismiss'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReminderModal;
