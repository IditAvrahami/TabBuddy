import React from 'react';
import './primitives.css';

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

const Container: React.FC<ContainerProps> = ({
  children,
  className = '',
  ...props
}) => {
  const combinedClass = `primitive-container ${className}`.trim();
  return (
    <div className={combinedClass} {...props}>
      {children}
    </div>
  );
};

export default Container;
