import React from 'react';
import { DependentSchedulePreview } from '../api';
import { convertUTCToLocalTime } from '../utils/timezone';
import Modal from './primitives/Modal';
import Container from './primitives/Container';
import Text from './primitives/Text';
import Button from './primitives/Button';
import './DeleteConfirmModal.css';

interface DeleteConfirmModalProps {
  visible: boolean;
  drugName: string;
  dependents: DependentSchedulePreview[];
  onConfirm: () => void;
  onCancel: () => void;
}

function formatNewTiming(dep: DependentSchedulePreview): string {
  if (dep.new_dependency_type === 'absolute' && dep.new_absolute_time) {
    const localTime = convertUTCToLocalTime(dep.new_absolute_time);
    return `Absolute at ${localTime} (local time)`;
  }
  if (dep.new_dependency_type === 'meal' && dep.new_depends_on_name) {
    const direction = dep.new_offset_minutes < 0 ? 'before' : 'after';
    return `${Math.abs(dep.new_offset_minutes)} min ${direction} ${dep.new_depends_on_name}`;
  }
  if (dep.new_dependency_type === 'drug' && dep.new_depends_on_name) {
    const direction = dep.new_offset_minutes < 0 ? 'before' : 'after';
    return `${Math.abs(dep.new_offset_minutes)} min ${direction} ${dep.new_depends_on_name}`;
  }
  return 'Independent schedule';
}

const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({
  visible,
  drugName,
  dependents,
  onConfirm,
  onCancel,
}) => {
  const hasDependents = dependents.length > 0;

  return (
    <Modal visible={visible} onClose={onCancel} className="delete-confirm-modal">
      <Container className="delete-confirm-header">
        <Text variant="h2" className="delete-confirm-title">
          Delete {drugName}?
        </Text>
        <Text variant="p" className="delete-confirm-subtitle">
          {hasDependents
            ? 'Deleting this medication schedule will affect other medications.'
            : 'Are you sure you want to delete this medication?'}
        </Text>
      </Container>

      {hasDependents && (
        <Container className="delete-confirm-deps">
          <Text variant="p" className="delete-confirm-label">
            The following medications depend on it:
          </Text>
          {dependents.map((dep) => (
            <Container key={dep.schedule_id} className="delete-confirm-dep-item">
              <Text variant="strong">{dep.drug_name}</Text>
              <Text variant="span" className="delete-confirm-current">
                Currently {dep.current_offset_minutes} min after {dep.current_depends_on_name}
              </Text>
              <Text variant="span" className="delete-confirm-arrow">
                &rarr;
              </Text>
              <Text variant="span" className="delete-confirm-new">
                {formatNewTiming(dep)}
              </Text>
            </Container>
          ))}
        </Container>
      )}

      <Container className="delete-confirm-actions">
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button variant="danger" onClick={onConfirm}>
          {hasDependents ? 'Delete and update schedule' : 'Delete'}
        </Button>
      </Container>
    </Modal>
  );
};

export default DeleteConfirmModal;
