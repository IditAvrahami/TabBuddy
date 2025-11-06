import React from 'react';
import Container from '../primitives/Container';
import './layout.css';

interface ErrorMessageProps {
  message: string;
  className?: string;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  className = ''
}) => {
  const combinedClass = `layout-error-message ${className}`.trim();
  return (
    <Container className={combinedClass}>
      {message}
    </Container>
  );
};

export default ErrorMessage;
