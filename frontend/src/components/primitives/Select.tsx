import React from 'react';
import Container from './Container';
import Text from './Text';
import './primitives.css';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
}

const Select: React.FC<SelectProps> = ({
  error,
  className = '',
  children,
  ...props
}) => {
  const baseClass = 'primitive-select';
  const errorClass = error ? 'primitive-select-error' : '';
  const combinedClass = `${baseClass} ${errorClass} ${className}`.trim();

  return (
    <Container className="primitive-select-wrapper">
      {React.createElement('select', { className: combinedClass, ...props }, children)}
      {error && <Text variant="span" className="primitive-select-error-message">{error}</Text>}
    </Container>
  );
};

export default Select;
