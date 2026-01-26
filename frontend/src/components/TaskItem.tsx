'use client';

import { Task } from '../lib/types';
import { format } from 'date-fns';

interface TaskItemProps {
  task: Task;
  onUpdate: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const handleToggleComplete = () => {
    onUpdate({ ...task, completed: !task.completed });
  };

  const handleEdit = () => {
    // Navigate to edit page
    window.location.href = `/tasks/${task.id}`;
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this task?')) {
      onDelete(task.id);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
      return dateString;
    }
  };

  return (
    <div className={`task-item p-4 border rounded-lg shadow-sm transition-all ${
      task.completed
        ? 'bg-gray-50 border-gray-200'
        : 'bg-white border-gray-300 hover:shadow-md'
    }`}>
      <div className="task-content">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className={`task-title text-lg font-semibold ${
              task.completed ? 'text-gray-500 line-through' : 'text-gray-900'
            }`}>
              {task.title}
            </h3>
            {task.description && (
              <p className={`task-description mt-1 text-sm ${
                task.completed ? 'text-gray-400' : 'text-gray-600'
              }`}>
                {task.description}
              </p>
            )}
            <div className="task-meta mt-2 text-xs text-gray-500 space-y-1">
              <span className="task-date">
                Created: {formatDate(task.created_at)}
              </span>
              {task.updated_at !== task.created_at && (
                <span className="task-date block">
                  Updated: {formatDate(task.updated_at)}
                </span>
              )}
            </div>
          </div>

          <div className="task-status ml-4 flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              task.completed
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {task.completed ? 'Completed' : 'Pending'}
            </span>
          </div>
        </div>
      </div>

      <div className="task-actions mt-4 flex justify-end space-x-2">
        <button
          onClick={handleToggleComplete}
          className={`task-toggle px-3 py-1 rounded-md text-sm font-medium transition-colors ${
            task.completed
              ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
          }`}
          aria-label={task.completed ? 'Mark incomplete' : 'Mark complete'}
        >
          {task.completed ? 'Mark Incomplete' : 'Mark Complete'}
        </button>

        <button
          onClick={handleEdit}
          className="task-edit px-3 py-1 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors"
          aria-label="Edit task"
        >
          Edit
        </button>

        <button
          onClick={handleDelete}
          className="task-delete px-3 py-1 bg-red-100 text-red-700 rounded-md text-sm font-medium hover:bg-red-200 transition-colors"
          aria-label="Delete task"
        >
          Delete
        </button>
      </div>
    </div>
  );
}