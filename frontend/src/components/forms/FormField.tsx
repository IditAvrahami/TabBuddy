import React from 'react';
import FormGroup from '../layout/FormGroup';
import Input from '../primitives/Input';
import Select from '../primitives/Select';
import DateInput from '../primitives/DateInput';
import TimeInput from '../primitives/TimeInput';

interface FormFieldProps {
  label: string;
  required?: boolean;
  error?: string;
  type?: 'text' | 'number' | 'select' | 'date' | 'time';
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  placeholder?: string;
  min?: number;
  children?: React.ReactNode; // For select options
  [key: string]: any; // Allow other input props
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  required = false,
  error,
  type = 'text',
  name,
  value,
  onChange,
  placeholder,
  min,
  children,
  ...otherProps
}) => {
  const commonProps = {
    name,
    value,
    onChange,
    error,
    placeholder,
    ...otherProps
  };

  let inputElement: React.ReactNode;

  switch (type) {
    case 'select':
      inputElement = (
        <Select {...commonProps}>
          {children}
        </Select>
      );
      break;
    case 'date':
      inputElement = <DateInput {...commonProps} />;
      break;
    case 'time':
      inputElement = <TimeInput {...commonProps} />;
      break;
    default:
      inputElement = (
        <Input
          type={type}
          min={min}
          {...commonProps}
        />
      );
  }

  return (
    <FormGroup label={label} required={required}>
      {inputElement}
    </FormGroup>
  );
};

export default FormField;
