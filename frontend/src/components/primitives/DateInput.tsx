import React from 'react';
import Input from './Input';

interface DateInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  error?: string;
}

const DateInput: React.FC<DateInputProps> = ({
  error,
  ...props
}) => {
  return <Input type="date" error={error} {...props} />;
};

export default DateInput;
