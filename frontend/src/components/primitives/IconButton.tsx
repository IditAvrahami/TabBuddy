import React from 'react';
import Icon from '../Icon';
import Button from './Button';

interface IconButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  iconName: 'pill' | 'edit' | 'delete' | 'hourglass' | 'meal' | 'tab-icon';
  iconSize?: number;
  variant?: 'primary' | 'secondary' | 'danger' | 'icon';
  title?: string;
}

const IconButton: React.FC<IconButtonProps> = ({
  iconName,
  iconSize = 20,
  variant = 'icon',
  title,
  className = '',
  ...props
}) => {
  return (
    <Button
      variant={variant}
      className={`primitive-icon-button ${className}`.trim()}
      title={title}
      {...props}
    >
      <Icon name={iconName} size={iconSize} />
    </Button>
  );
};

export default IconButton;
