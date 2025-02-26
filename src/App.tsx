import React, { useState, useMemo, useEffect } from 'react';
import { BarChart, SlidersHorizontal } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ModelResult, data } from './types';

// Replace this with your actual GitHub username
const GITHUB_USERNAME = '@Ollivvt';

function App() {
  const [selectedFilters, setSelectedFilters] = useState({
    dataset: 'Mammo',
    model: 'EfficientNetB3',
    comparisonType: 'Image Size',
    metric: 'F1-score',
  });

  // Get available options based on current selections
  const availableOptions = useMemo(() => {
    const datasets = Array.from(new Set(data.map(item => item.Dataset)));
    
    const models = Array.from(
      new Set(
        data
          .filter(item => item.Dataset === selectedFilters.dataset)
          .map(item => item.Model)
      )
    );

    const experimentTypes = Array.from(
      new Set(
        data
          .filter(item => 
            item.Dataset === selectedFilters.dataset && 
            item.Model === selectedFilters.model
          )
          .map(item => item['Experiment Type'])
      )
    );

    const imageSizes = Array.from(
      new Set(
        data
          .filter(item => 
            item.Dataset === selectedFilters.dataset && 
            item.Model === selectedFilters.model &&
            item['Experiment Type'] === 'Original Data'
          )
          .map(item => item.ImageSize)
      )
    );

    // Determine available comparison types based on dataset and model
    let comparisonTypes = [];
    
    if (selectedFilters.dataset === 'BDen') {
      // BDen only has experiment type comparison
      comparisonTypes = ['Experiment Type'];
    } else if (selectedFilters.model === 'DINOv2') {
      // DINOv2 only has image size comparison
      comparisonTypes = ['Image Size'];
    } else {
      // For Mammo dataset with other models, allow both comparisons
      comparisonTypes = imageSizes.length > 1 ? ['Image Size', 'Experiment Type'] : ['Experiment Type'];
    }

    return {
      datasets,
      models,
      experimentTypes,
      comparisonTypes,
      imageSizes,
    };
  }, [selectedFilters.dataset, selectedFilters.model]);

  // Update selections when available options change
  useEffect(() => {
    setSelectedFilters(prev => {
      const updates = {};

      // If current model is not available for selected dataset
      if (!availableOptions.models.includes(prev.model)) {
        updates.model = availableOptions.models[0];
      }

      // If current comparison type is not available
      if (!availableOptions.comparisonTypes.includes(prev.comparisonType)) {
        updates.comparisonType = availableOptions.comparisonTypes[0];
      }

      return Object.keys(updates).length > 0 
        ? { ...prev, ...updates }
        : prev;
    });
  }, [availableOptions]);

  const filteredData = useMemo(() => {
    return data.filter(
      (item) =>
        item.Dataset === selectedFilters.dataset &&
        item.Model === selectedFilters.model &&
        (selectedFilters.comparisonType === 'Image Size' 
          ? item['Experiment Type'] === 'Original Data'
          : item.ImageSize === '512x512' && item.Manufacturer === 'All')
    );
  }, [selectedFilters]);

  const chartData = useMemo(() => {
    const groupedData = filteredData.reduce((acc, item) => {
      const key = selectedFilters.comparisonType === 'Image Size' 
        ? item.ImageSize 
        : item['Experiment Type'];
      
      if (!acc[key]) {
        acc[key] = {
          name: key,
          'Asian - East and Southeast': 0,
          'Asian - South': 0,
          'White': 0
        };
      }
      
      acc[key][item.Class] = item[selectedFilters.metric];
      return acc;
    }, {});

    return Object.values(groupedData);
  }, [filteredData, selectedFilters.metric, selectedFilters.comparisonType]);

  const metrics = ['Precision', 'Recall (Sensitivity)', 'Specificity', 'F1-score'];

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <div className="flex-grow p-8">
        <div className="max-w-7xl mx-auto">
          <header className="mb-8">
            <div className="flex items-center gap-3">
              <BarChart className="w-8 h-8 text-indigo-600" />
              <h1 className="text-3xl font-bold text-gray-900">AI Ethnicity Model Performance Analysis</h1>
            </div>
            <p className="mt-2 text-gray-600">
              Compare model performance across different classes and parameters
            </p>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white p-6 rounded-lg shadow-lg">
                <div className="flex items-center gap-2 mb-4">
                  <SlidersHorizontal className="w-5 h-5 text-indigo-600" />
                  <h2 className="text-lg font-semibold">Filters</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Dataset</label>
                    <select
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                      value={selectedFilters.dataset}
                      onChange={(e) => setSelectedFilters(prev => ({ ...prev, dataset: e.target.value }))}
                    >
                      {availableOptions.datasets.map(dataset => (
                        <option key={dataset} value={dataset}>{dataset}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                    <select
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                      value={selectedFilters.model}
                      onChange={(e) => setSelectedFilters(prev => ({ ...prev, model: e.target.value }))}
                    >
                      {availableOptions.models.map(model => (
                        <option key={model} value={model}>{model}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Compare By</label>
                    <select
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                      value={selectedFilters.comparisonType}
                      onChange={(e) => setSelectedFilters(prev => ({ ...prev, comparisonType: e.target.value }))}
                    >
                      {availableOptions.comparisonTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Metric</label>
                    <select
                      className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                      value={selectedFilters.metric}
                      onChange={(e) => setSelectedFilters(prev => ({ ...prev, metric: e.target.value }))}
                    >
                      {metrics.map(metric => (
                        <option key={metric} value={metric}>{metric}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-lg">
                <h2 className="text-lg font-semibold mb-4">Legend</h2>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-indigo-500 rounded"></div>
                    <span>Asian - East and Southeast</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-emerald-500 rounded"></div>
                    <span>Asian - South</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-amber-500 rounded"></div>
                    <span>White</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="lg:col-span-3">
              <div className="bg-white p-6 rounded-lg shadow-lg">
                <h2 className="text-xl font-bold mb-6">
                  {selectedFilters.metric} by {selectedFilters.comparisonType}
                </h2>
                <div className="h-[500px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart 
                      data={chartData} 
                      margin={{ top: 20, right: 30, left: 20, bottom: 65 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="name" 
                        angle={-45}
                        textAnchor="end"
                        height={60}
                        interval={0}
                      />
                      <YAxis 
                        domain={[0, 1]} 
                        tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                        width={80}
                      />
                      <Tooltip 
                        formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`}
                      />
                      <Legend 
                        verticalAlign="top"
                        height={36}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="Asian - East and Southeast" 
                        stroke="#6366f1" 
                        strokeWidth={2}
                        dot={{ r: 4 }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="Asian - South" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        dot={{ r: 4 }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="White" 
                        stroke="#f59e0b" 
                        strokeWidth={2}
                        dot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <footer className="bg-gray-800 text-gray-300 py-6 mt-8">
        <div className="max-w-7xl mx-auto px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm">
                © 2025 <a href={`https://github.com/${GITHUB_USERNAME}`} className="text-indigo-400 hover:text-indigo-300 transition-colors" target="_blank" rel="noopener noreferrer">{GITHUB_USERNAME}</a>
              </p>
              <p className="text-sm mt-1">
                MSc Computer Science, University of British Columbia
              </p>
            </div>
            <div className="md:text-right">
              <p className="text-sm">
                In collaboration with BC Cancer
              </p>
              <p className="text-sm mt-1">
                All rights reserved
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;