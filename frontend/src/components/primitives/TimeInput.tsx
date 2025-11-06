import React from 'react';
import Input from './Input';

interface TimeInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  error?: string;
}

const TimeInput: React.FC<TimeInputProps> = ({
  error,
  ...props
}) => {
  return <Input type="time" error={error} {...props} />;
};

export default TimeInput;
