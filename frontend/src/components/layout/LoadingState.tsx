import React from 'react';
import Container from '../primitives/Container';
import Text from '../primitives/Text';
import Icon from '../Icon';
import './layout.css';

interface LoadingStateProps {
  message?: string;
  iconSize?: number;
}

const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading...',
  iconSize = 32
}) => {
  return (
    <Container className="layout-loading-state">
      <Container className="layout-loading-state-icon">
        <Icon name="hourglass" size={iconSize} />
      </Container>
      <Text variant="p">{message}</Text>
    </Container>
  );
};

export default LoadingState;
