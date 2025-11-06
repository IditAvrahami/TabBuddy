import React from 'react';
import FormField from './FormField';
import Option from '../primitives/Option';
import { DrugDto } from '../../api';

interface DrugDependencyFieldsProps {
  existingDrugs: DrugDto[];
  dependsOnDrugId: string;
  drugOffsetMinutes: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
}

const DrugDependencyFields: React.FC<DrugDependencyFieldsProps> = ({
  existingDrugs,
  dependsOnDrugId,
  drugOffsetMinutes,
  onChange,
}) => {
  return (
    <>
      <FormField
        label="Depends on Drug"
        type="select"
        name="dependsOnDrugId"
        value={dependsOnDrugId}
        onChange={onChange}
        required
      >
        <Option value="">Select drug</Option>
        {existingDrugs.map(drug => (
          <Option key={drug.id} value={drug.id}>
            {drug.name}
          </Option>
        ))}
      </FormField>
      <FormField
        label="Offset (minutes)"
        type="number"
        name="drugOffsetMinutes"
        value={drugOffsetMinutes}
        onChange={onChange}
        placeholder="Minutes after dependent drug"
        required
      />
    </>
  );
};

export default DrugDependencyFields;
