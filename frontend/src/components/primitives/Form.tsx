import React from 'react';
import './primitives.css';

interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children: React.ReactNode;
  className?: string;
}

const Form: React.FC<FormProps> = ({
  children,
  className = '',
  ...props
}) => {
  const combinedClass = `primitive-form ${className}`.trim();
  return (
    <form className={combinedClass} {...props}>
      {children}
    </form>
  );
};

export default Form;
