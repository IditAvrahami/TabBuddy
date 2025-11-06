import React from 'react';
import Container from '../primitives/Container';
import Text from '../primitives/Text';
import FormField from './FormField';
import { convertLocalTimeToUTC, formatTimeWithTimezone } from '../../utils/timezone';

interface AbsoluteTimeFieldProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
}

const AbsoluteTimeField: React.FC<AbsoluteTimeFieldProps> = ({ value, onChange }) => {
  return (
    <>
      <FormField
        label="Time of Day (Local Time)"
        type="time"
        name="absoluteTime"
        value={value}
        onChange={onChange}
        required
      />
      {value && (
        <Container className="timezone-hint">
          <Text variant="p">
            Will be stored as: {formatTimeWithTimezone(convertLocalTimeToUTC(value), true)}
          </Text>
        </Container>
      )}
    </>
  );
};

export default AbsoluteTimeField;
