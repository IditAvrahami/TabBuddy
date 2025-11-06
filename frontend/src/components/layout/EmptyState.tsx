import React from 'react';
import Container from '../primitives/Container';
import Text from '../primitives/Text';
import Icon from '../Icon';
import './layout.css';

interface EmptyStateProps {
  icon: 'pill' | 'edit' | 'delete' | 'hourglass' | 'meal' | 'tab-icon';
  iconSize?: number;
  title: string;
  message: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  iconSize = 48,
  title,
  message
}) => {
  return (
    <Container className="layout-empty-state">
      <Container className="layout-empty-state-icon">
        <Icon name={icon} size={iconSize} />
      </Container>
      <Text variant="h3" className="layout-empty-state-title">{title}</Text>
      <Text variant="p" className="layout-empty-state-text">{message}</Text>
    </Container>
  );
};

export default EmptyState;
