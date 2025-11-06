import React from 'react';
import Container from './Container';
import './primitives.css';

interface ModalProps {
  visible: boolean;
  onClose?: () => void;
  children: React.ReactNode;
  className?: string;
}

const Modal: React.FC<ModalProps> = ({
  visible,
  onClose,
  children,
  className = ''
}) => {
  if (!visible) return null;

  const handleOverlayClick = (e: React.MouseEvent<HTMLElement>) => {
    if (e.target === e.currentTarget && onClose) {
      onClose();
    }
  };

  const containerClass = `primitive-modal-container ${className}`.trim();

  return (
    <Container className="primitive-modal-overlay" onClick={handleOverlayClick}>
      <Container className={containerClass}>
        {children}
      </Container>
    </Container>
  );
};

export default Modal;
