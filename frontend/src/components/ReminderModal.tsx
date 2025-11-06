import React, { useState } from 'react';
import { NotificationDto } from '../api';
import Modal from './primitives/Modal';
import Container from './primitives/Container';
import Text from './primitives/Text';
import Button from './primitives/Button';
import Select from './primitives/Select';
import Option from './primitives/Option';
import FormGroup from './layout/FormGroup';
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

  if (!notification) {
    return null;
  }

  const handleSnooze = async () => {
    if (isProcessing || !notification) return;

    setIsProcessing(true);
    try {
      await onSnooze(notification.schedule_id, snoozeMinutes);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDismiss = async () => {
    if (isProcessing || !notification) return;

    setIsProcessing(true);
    try {
      await onDismiss(notification.schedule_id);
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
    <Modal visible={visible} onClose={onClose} className="reminder-modal">
      <Container className="reminder-modal-header">
        <Text variant="h2" className="reminder-modal-title">
          <Icon name="pill" size={24} />
          Time to take your medication
        </Text>
        <Text variant="p" className="reminder-modal-time">
          {formatTime(notification.scheduled_time)}
        </Text>
      </Container>

      <Container className="reminder-modal-drug-info">
        <Container className="reminder-modal-drug-name">
          <Text variant="strong">{notification.drug_name}</Text>
        </Container>
        <Container className="reminder-modal-drug-details">
          {notification.amount_per_dose} {notification.kind === 'pill' ? 'pill(s)' : 'ml'}
          {notification.dependency_type === 'absolute' && ' at scheduled time'}
        </Container>
      </Container>

      <FormGroup label="Snooze for:">
        <Select
          value={snoozeMinutes.toString()}
          onChange={(e) => setSnoozeMinutes(Number(e.target.value))}
        >
          <Option value={5}>5 minutes</Option>
          <Option value={10}>10 minutes</Option>
          <Option value={15}>15 minutes</Option>
          <Option value={30}>30 minutes</Option>
          <Option value={60}>1 hour</Option>
        </Select>
      </FormGroup>

      <Container className="reminder-modal-actions">
        <Button
          variant="primary"
          onClick={handleSnooze}
          disabled={isProcessing}
          className="reminder-modal-button snooze-button"
        >
          {isProcessing ? 'Processing...' : 'Snooze'}
        </Button>
        <Button
          variant="danger"
          onClick={handleDismiss}
          disabled={isProcessing}
          className="reminder-modal-button dismiss-button"
        >
          {isProcessing ? 'Processing...' : 'Dismiss'}
        </Button>
      </Container>
    </Modal>
  );
};

export default ReminderModal;
