import React from 'react';
import { ModelResult } from '../types';

interface FilterPanelProps {
  data: ModelResult[];
  selectedFilters: {
    dataset: string;
    model: string;
    experimentType: string;
    class: string;
  };
  onFilterChange: (filterType: string, value: string) => void;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  data,
  selectedFilters,
  onFilterChange,
}) => {
  const getUniqueValues = (key: keyof ModelResult) => {
    return Array.from(new Set(data.map((item) => item[key])));
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-lg font-semibold mb-4">Filters</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Dataset</label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            value={selectedFilters.dataset}
            onChange={(e) => onFilterChange('dataset', e.target.value)}
          >
            {getUniqueValues('Dataset').map((dataset) => (
              <option key={dataset} value={dataset}>
                {dataset}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Model</label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            value={selectedFilters.model}
            onChange={(e) => onFilterChange('model', e.target.value)}
          >
            {getUniqueValues('Model').map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Experiment Type</label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            value={selectedFilters.experimentType}
            onChange={(e) => onFilterChange('experimentType', e.target.value)}
          >
            {getUniqueValues('Experiment Type').map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Class</label>
          <select
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            value={selectedFilters.class}
            onChange={(e) => onFilterChange('class', e.target.value)}
          >
            {getUniqueValues('Class').map((cls) => (
              <option key={cls} value={cls}>
                {cls}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};