import React, { useState } from 'react';
import { NotificationDto } from '../api';

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
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '24px',
        maxWidth: '400px',
        width: '90%',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
        fontFamily: 'Nunito, Quicksand, sans-serif',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <h2 style={{ 
            margin: '0 0 8px 0', 
            color: '#2c3e50',
            fontSize: '20px',
            fontWeight: '600'
          }}>
            💊 Time to take your medication
          </h2>
          <p style={{ 
            margin: '0', 
            color: '#7f8c8d',
            fontSize: '14px'
          }}>
            {formatTime(notification.scheduled_time)}
          </p>
        </div>

        <div style={{ 
          backgroundColor: '#f8f9fa', 
          padding: '16px', 
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <div style={{ marginBottom: '8px' }}>
            <strong style={{ color: '#2c3e50' }}>{notification.drug_name}</strong>
          </div>
          <div style={{ color: '#7f8c8d', fontSize: '14px' }}>
            {notification.amount_per_dose} {notification.kind === 'pill' ? 'pill(s)' : 'ml'} 
            {notification.dependency_type === 'absolute' && ' at scheduled time'}
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '8px', 
            color: '#2c3e50',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            Snooze for:
          </label>
          <select
            value={snoozeMinutes}
            onChange={(e) => setSnoozeMinutes(Number(e.target.value))}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #ddd',
              borderRadius: '6px',
              fontSize: '14px',
              backgroundColor: 'white',
            }}
          >
            <option value={5}>5 minutes</option>
            <option value={10}>10 minutes</option>
            <option value={15}>15 minutes</option>
            <option value={30}>30 minutes</option>
            <option value={60}>1 hour</option>
          </select>
        </div>

        <div style={{ 
          display: 'flex', 
          gap: '12px',
          justifyContent: 'flex-end'
        }}>
          <button
            onClick={handleSnooze}
            disabled={isProcessing}
            style={{
              padding: '10px 20px',
              backgroundColor: isProcessing ? '#95a5a6' : '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: isProcessing ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'background-color 0.2s',
              opacity: isProcessing ? 0.6 : 1,
            }}
            onMouseOver={(e) => {
              if (!isProcessing) e.currentTarget.style.backgroundColor = '#2980b9';
            }}
            onMouseOut={(e) => {
              if (!isProcessing) e.currentTarget.style.backgroundColor = '#3498db';
            }}
          >
            {isProcessing ? 'Processing...' : 'Snooze'}
          </button>
          <button
            onClick={handleDismiss}
            disabled={isProcessing}
            style={{
              padding: '10px 20px',
              backgroundColor: isProcessing ? '#95a5a6' : '#e74c3c',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: isProcessing ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              transition: 'background-color 0.2s',
              opacity: isProcessing ? 0.6 : 1,
            }}
            onMouseOver={(e) => {
              if (!isProcessing) e.currentTarget.style.backgroundColor = '#c0392b';
            }}
            onMouseOut={(e) => {
              if (!isProcessing) e.currentTarget.style.backgroundColor = '#e74c3c';
            }}
          >
            {isProcessing ? 'Processing...' : 'Dismiss'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReminderModal;
