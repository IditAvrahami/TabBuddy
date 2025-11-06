import React from 'react';
import Container from '../primitives/Container';
import Button from '../primitives/Button';
import './layout.css';

interface FormActionsProps {
  onCancel: () => void;
  onSubmit?: () => void;
  submitLabel?: string;
  cancelLabel?: string;
  loading?: boolean;
  className?: string;
}

const FormActions: React.FC<FormActionsProps> = ({
  onCancel,
  onSubmit,
  submitLabel = 'Submit',
  cancelLabel = 'Cancel',
  loading = false,
  className = ''
}) => {
  const combinedClass = `layout-form-actions ${className}`.trim();
  return (
    <Container className={combinedClass}>
      <Button
        type="button"
        variant="secondary"
        onClick={onCancel}
        className="layout-form-button-cancel"
      >
        {cancelLabel}
      </Button>
      <Button
        type="submit"
        variant="primary"
        disabled={loading}
        className="layout-form-button-submit"
      >
        {loading ? 'Processing...' : submitLabel}
      </Button>
    </Container>
  );
};

export default FormActions;
