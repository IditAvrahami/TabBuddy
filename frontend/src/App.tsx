import React, { useEffect, useState } from 'react';
import './App.css';
import { api, type DrugDto, type DrugCreateDto, type NotificationDto } from './api';
import Container from './components/primitives/Container';
import Navbar from './components/Navbar';
import DrugList from './components/DrugList';
import DrugForm from './components/DrugForm';
import Settings from './components/Settings';
import ReminderModal from './components/ReminderModal';

function App() {
  const [activeTab, setActiveTab] = useState<'drugs' | 'settings'>('drugs');
  const [showDrugForm, setShowDrugForm] = useState(false);
  const [editingDrug, setEditingDrug] = useState<DrugDto | null>(null);
  const [drugs, setDrugs] = useState<DrugDto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Notification state
  const [activeNotification, setActiveNotification] = useState<NotificationDto | null>(null);
  const [notificationQueue, setNotificationQueue] = useState<NotificationDto[]>([]);
  const [pollTimer, setPollTimer] = useState<NodeJS.Timeout | null>(null);

  const loadDrugs = async () => {
    try {
      setLoading(true);
      setError(null);
      const list = await api.listDrugs();
      setDrugs(list);
    } catch (err: any) {
      const errorMessage = err?.message || err?.toString() || 'Failed to load drugs';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Notification polling
  const pollNotifications = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const notifications = await api.getNotifications(today);

      console.log(`Polling notifications: ${notifications.length} due now`);

      // Backend handles all timing logic - just add new notifications to queue
      setNotificationQueue(prev => {
        const existingIds = new Set(prev.map(n => n.schedule_id));
        const newNotifications = notifications.filter(n => !existingIds.has(n.schedule_id));

        if (newNotifications.length > 0) {
          console.log(`Adding ${newNotifications.length} new notifications to queue`);
        }
        return [...prev, ...newNotifications];
      });
    } catch (err) {
      console.error('Failed to poll notifications:', err);
    }
  };

  // Show next notification in queue
  const showNextNotification = () => {
    console.log(`showNextNotification: queue=${notificationQueue.length}, active=${!!activeNotification}`);
    if (notificationQueue.length > 0 && !activeNotification) {
      const next = notificationQueue[0];
      console.log(`Showing notification: ${next.drug_name} at ${next.scheduled_time}`);
      setActiveNotification(next);
      setNotificationQueue(prev => prev.slice(1));
    }
  };

  // Handle notification actions
  const handleSnooze = async (scheduleId: number, minutes: number) => {
    try {
      const today = new Date().toISOString().split('T')[0];
      await api.snoozeNotification(scheduleId, minutes, today);
      console.log(`Snoozed notification for ${minutes} minutes`);

      // Remove from queue - the notification will reappear when backend says it's time
      setNotificationQueue(prev => prev.filter(n => n.schedule_id !== scheduleId));

      // Close the modal
      setActiveNotification(null);

    } catch (err) {
      console.error('Failed to snooze notification:', err);
    }
  };

  const handleDismiss = async (scheduleId: number) => {
    try {
      const today = new Date().toISOString().split('T')[0];
      await api.dismissNotification(scheduleId, today);
      console.log('Dismissed notification');

      // Remove from queue permanently
      setNotificationQueue(prev => prev.filter(n => n.schedule_id !== scheduleId));

      // Close the modal
      setActiveNotification(null);

    } catch (err) {
      console.error('Failed to dismiss notification:', err);
    }
  };

  const closeNotification = () => {
    setActiveNotification(null);
  };

  useEffect(() => {
    loadDrugs();

    // Start polling for notifications every 5 seconds (for testing)
    const timer = setInterval(pollNotifications, 5000);
    setPollTimer(timer);

    // Initial poll
    pollNotifications();

    return () => {
      if (timer) clearInterval(timer);
    };
  }, []);

  // Show next notification when queue changes
  useEffect(() => {
    showNextNotification();
  }, [notificationQueue, activeNotification]);

  const handleAddDrug = async (drug: DrugCreateDto) => {
    try {
      setLoading(true);
      setError(null);
      await api.addDrug(drug);
      await loadDrugs();
      setShowDrugForm(false);
      setEditingDrug(null);
    } catch (err: any) {
      const errorMessage = err?.message || err?.toString() || 'Failed to add drug';
      setError(errorMessage);
      throw err; // Re-throw to let DrugForm handle the error display
    } finally {
      setLoading(false);
    }
  };

  const handleEditDrug = async (drug: DrugCreateDto) => {
    try {
      setLoading(true);
      setError(null);
      await api.updateDrug(editingDrug!.id, drug);
      await loadDrugs();
      setShowDrugForm(false);
      setEditingDrug(null);
    } catch (err: any) {
      const errorMessage = err?.message || err?.toString() || 'Failed to update drug';
      setError(errorMessage);
      throw err; // Re-throw to let DrugForm handle the error display
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDrug = async (drugId: number) => {
    try {
      setLoading(true);
      setError(null);
      await api.deleteDrug(drugId);
      await loadDrugs();
    } catch (err: any) {
      const errorMessage = err?.message || err?.toString() || 'Failed to delete drug';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const openEditForm = (drug: DrugDto) => {
    setEditingDrug(drug);
    setShowDrugForm(true);
  };

  const openAddForm = () => {
    setEditingDrug(null);
    setShowDrugForm(true);
  };

  const closeForm = () => {
    setShowDrugForm(false);
    setEditingDrug(null);
  };

  return (
    <Container className="App">
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === 'drugs' ? (
        <DrugList
          drugs={drugs}
          loading={loading}
          error={error}
          onAddDrug={openAddForm}
          onEditDrug={openEditForm}
          onDeleteDrug={handleDeleteDrug}
        />
      ) : (
        <Settings />
      )}

      {showDrugForm && (
        <DrugForm
          onSubmit={editingDrug ? handleEditDrug : handleAddDrug}
          onCancel={closeForm}
          loading={loading}
          editingDrug={editingDrug}
        />
      )}

      <ReminderModal
        visible={!!activeNotification}
        notification={activeNotification}
        onSnooze={handleSnooze}
        onDismiss={handleDismiss}
        onClose={closeNotification}
      />
    </Container>
  );
}

export default App;
