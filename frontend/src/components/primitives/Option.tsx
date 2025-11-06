import React from 'react';

interface OptionProps extends React.OptionHTMLAttributes<HTMLOptionElement> {
  children: React.ReactNode;
  value: string | number;
}

const Option: React.FC<OptionProps> = ({
  children,
  value,
  ...props
}) => {
  return React.createElement('option', { value, ...props }, children);
};

export default Option;
