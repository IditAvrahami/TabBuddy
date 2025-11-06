import React from 'react';
import FormField from './FormField';
import Option from '../primitives/Option';
import { DependencyType } from '../../api';

interface DependencySelectorProps {
  value: DependencyType;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
}

const DependencySelector: React.FC<DependencySelectorProps> = ({ value, onChange }) => {
  return (
    <FormField
      label="Timing Dependency"
      type="select"
      name="dependencyType"
      value={value}
      onChange={onChange}
      required
    >
      <Option value="independent">Independent (no dependency)</Option>
      <Option value="absolute">Absolute time</Option>
      <Option value="meal">Depends on meal</Option>
      <Option value="drug">Depends on another drug</Option>
    </FormField>
  );
};

export default DependencySelector;
