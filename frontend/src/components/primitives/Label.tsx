import React from 'react';
import './primitives.css';

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  children: React.ReactNode;
  className?: string;
}

const Label: React.FC<LabelProps> = ({
  children,
  className = '',
  ...props
}) => {
  const combinedClass = `primitive-label ${className}`.trim();
  return (
    <label className={combinedClass} {...props}>
      {children}
    </label>
  );
};

export default Label;
