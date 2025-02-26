import React from 'react';
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
import { ModelResult } from '../types';

interface MetricsChartProps {
  data: ModelResult[];
  title: string;
}

export const MetricsChart: React.FC<MetricsChartProps> = ({ data, title }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">{title}</h2>
      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="ImageSize" />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Precision" stroke="#8884d8" />
            <Line type="monotone" dataKey="Recall (Sensitivity)" stroke="#82ca9d" />
            <Line type="monotone" dataKey="Specificity" stroke="#ffc658" />
            <Line type="monotone" dataKey="F1-score" stroke="#ff7300" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};