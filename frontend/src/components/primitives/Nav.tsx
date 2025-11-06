import React from 'react';
import './primitives.css';

interface NavProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
  className?: string;
}

const Nav: React.FC<NavProps> = ({
  children,
  className = '',
  ...props
}) => {
  const combinedClass = `primitive-nav ${className}`.trim();
  return React.createElement('nav', { className: combinedClass, ...props }, children);
};

export default Nav;
