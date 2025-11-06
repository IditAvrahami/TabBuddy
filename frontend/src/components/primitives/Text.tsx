import React from 'react';
import './primitives.css';

type TextVariant = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span' | 'strong' | 'em';

interface TextProps {
  variant?: TextVariant;
  children?: React.ReactNode;
  className?: string;
  [key: string]: any; // Allow other props
}

const Text: React.FC<TextProps> = ({
  variant = 'p',
  children,
  className = '',
  ...props
}) => {
  const baseClass = 'primitive-text';
  const variantClass = `primitive-text-${variant}`;
  const combinedClass = `${baseClass} ${variantClass} ${className}`.trim();

  const components: Record<TextVariant, keyof React.JSX.IntrinsicElements> = {
    h1: 'h1',
    h2: 'h2',
    h3: 'h3',
    h4: 'h4',
    h5: 'h5',
    h6: 'h6',
    p: 'p',
    span: 'span',
    strong: 'strong',
    em: 'em',
  };

  const Tag = components[variant];

  return React.createElement(Tag, { className: combinedClass, ...props }, children);
};

export default Text;
