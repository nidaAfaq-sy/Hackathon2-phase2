'use client';

import { useState, useEffect } from 'react';
import { Task, TaskFilter as TaskFilterType } from '../lib/types';
import TaskItem from './TaskItem';
import TaskFilter from './TaskFilter';
import TaskSearch from './TaskSearch';
import EmptyState from './EmptyState';
import LoadingSpinner from './LoadingSpinner';

interface TaskListProps {
  userId: string;
  tasks: Task[];
  onTaskUpdate: (task: Task) => void;
  onTaskDelete: (taskId: string) => void;
  loading?: boolean;
  error?: string | null;
}

export default function TaskList({
  userId,
  tasks,
  onTaskUpdate,
  onTaskDelete,
  loading = false,
  error = null,
}: TaskListProps) {
  const [filter, setFilter] = useState<TaskFilterType>({});
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTasks = tasks.filter(task => {
    // Filter by completion status
    if (filter.completed !== undefined && task.completed !== filter.completed) {
      return false;
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        task.title.toLowerCase().includes(query) ||
        (task.description && task.description.toLowerCase().includes(query))
      );
    }

    return true;
  });

  const handleTaskUpdate = (task: Task) => {
    onTaskUpdate(task);
  };

  const handleTaskDelete = (taskId: string) => {
    onTaskDelete(taskId);
  };

  return (
    <div className="task-list space-y-4">
      {/* Header with controls */}
      <div className="task-list-header flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          <TaskFilter currentFilter={filter} onFilterChange={setFilter} />
          <TaskSearch value={searchQuery} onChange={setSearchQuery} />
        </div>
      </div>

      {/* Task items */}
      <div className="task-items space-y-2">
        {loading ? (
          <LoadingSpinner />
        ) : filteredTasks.length === 0 ? (
          <EmptyState
            title={searchQuery || filter.completed !== undefined ? "No tasks found" : "No tasks yet"}
            description={
              searchQuery || filter.completed !== undefined
                ? "Try adjusting your search or filter criteria"
                : "Create your first task to get started"
            }
            actionText={searchQuery || filter.completed !== undefined ? "Clear filters" : "Create Task"}
            onAction={() => {
              if (searchQuery || filter.completed !== undefined) {
                setSearchQuery('');
                setFilter({});
              }
            }}
          />
        ) : (
          filteredTasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onUpdate={handleTaskUpdate}
              onDelete={handleTaskDelete}
            />
          ))
        )}
      </div>
    </div>
  );
}