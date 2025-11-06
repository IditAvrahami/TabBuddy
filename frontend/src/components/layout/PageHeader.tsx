import React from 'react';
import Container from '../primitives/Container';
import Text from '../primitives/Text';
import Button from '../primitives/Button';
import './layout.css';

interface PageHeaderProps {
  title: string;
  actionButton?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
}

const PageHeader: React.FC<PageHeaderProps> = ({ title, actionButton }) => {
  return (
    <Container className="layout-page-header">
      <Text variant="h2" className="layout-page-title">{title}</Text>
      {actionButton && (
        <Button
          variant="primary"
          onClick={actionButton.onClick}
          className="layout-page-action-button"
        >
          {actionButton.icon && <Text variant="span" className="layout-page-action-icon">{actionButton.icon}</Text>}
          {actionButton.label}
        </Button>
      )}
    </Container>
  );
};

export default PageHeader;
