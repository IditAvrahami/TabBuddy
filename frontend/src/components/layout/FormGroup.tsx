import React from 'react';
import Container from '../primitives/Container';
import Label from '../primitives/Label';
import './layout.css';

interface FormGroupProps {
  label: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}

const FormGroup: React.FC<FormGroupProps> = ({
  label,
  required = false,
  children,
  className = ''
}) => {
  const combinedClass = `layout-form-group ${className}`.trim();
  return (
    <Container className={combinedClass}>
      <Label className="layout-form-label">
        {label} {required && '*'}
      </Label>
      {children}
    </Container>
  );
};

export default FormGroup;
