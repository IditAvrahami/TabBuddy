import React from 'react';
import Container from './Container';
import Text from './Text';
import './primitives.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

const Input: React.FC<InputProps> = ({
  error,
  className = '',
  ...props
}) => {
  const baseClass = 'primitive-input';
  const errorClass = error ? 'primitive-input-error' : '';
  const combinedClass = `${baseClass} ${errorClass} ${className}`.trim();

  return (
    <Container className="primitive-input-wrapper">
      {React.createElement('input', { className: combinedClass, ...props })}
      {error && <Text variant="span" className="primitive-input-error-message">{error}</Text>}
    </Container>
  );
};

export default Input;
