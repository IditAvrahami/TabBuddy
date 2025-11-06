import React from 'react';
import pillIcon from '../assets/icons/pill.svg';
import editIcon from '../assets/icons/edit.svg';
import deleteIcon from '../assets/icons/delete.svg';
import hourglassIcon from '../assets/icons/hourglass.svg';
import mealIcon from '../assets/icons/meal.svg';
import tabIcon from '../assets/icons/tab-icon.svg';

interface IconProps {
  name: 'pill' | 'edit' | 'delete' | 'hourglass' | 'meal' | 'tab-icon';
  className?: string;
  size?: number;
}

const Icon: React.FC<IconProps> = ({ name, className, size = 24 }) => {
  const iconMap: Record<string, string> = {
    'pill': pillIcon,
    'edit': editIcon,
    'delete': deleteIcon,
    'hourglass': hourglassIcon,
    'meal': mealIcon,
    'tab-icon': tabIcon,
  };

  return (
    <img
      src={iconMap[name]}
      alt={name}
      className={className}
      style={{ width: size, height: size }}
    />
  );
};

export default Icon;
