import React from 'react';
import './primitives.css';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, className = '' }) => {
  const baseClass = 'primitive-card';
  const combinedClass = `${baseClass} ${className}`.trim();

  return (
    <div className={combinedClass}>
      {children}
    </div>
  );
};

export default Card;
