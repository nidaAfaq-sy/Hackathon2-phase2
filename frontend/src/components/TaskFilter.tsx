'use client';

import { TaskFilter } from '../lib/types';

interface TaskFilterProps {
  currentFilter: TaskFilter;
  onFilterChange: (filter: TaskFilter) => void;
}

export default function TaskFilter({ currentFilter, onFilterChange }: TaskFilterProps) {
  const filters = [
    { value: undefined, label: 'All', count: null },
    { value: false, label: 'Active', count: null },
    { value: true, label: 'Completed', count: null },
  ];

  return (
    <div className="task-filter bg-white border border-gray-300 rounded-lg p-1 flex space-x-1">
      {filters.map((filter) => (
        <button
          key={filter.value ?? 'all'}
          onClick={() => onFilterChange({ ...currentFilter, completed: filter.value })}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            currentFilter.completed === filter.value
              ? 'bg-blue-500 text-white'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
        >
          {filter.label}
          {filter.count !== null && (
            <span className="ml-2 bg-gray-200 text-gray-700 px-2 py-0.5 rounded-full text-xs">
              {filter.count}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}