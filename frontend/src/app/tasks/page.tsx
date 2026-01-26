'use client';

import { useSession } from '../../lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiClient } from '../../lib/api';
import { Task, TaskFilter } from '../../lib/types';
import TaskList from '../../components/TaskList';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export default function TasksPage() {
  const { data: session, isPending } = useSession();
  const status = isPending ? 'loading' : session ? 'authenticated' : 'unauthenticated';
  const router = useRouter();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<TaskFilter>({});
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (status === 'loading') return;

    if (session) {
      fetchTasks();
    }
  }, [session, status]);

  const fetchTasks = async () => {
    if (!session?.user?.id) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.getTasks(session.user.id, filter);
      setTasks(response.tasks);
    } catch (err) {
      setError('Failed to load tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskUpdate = async (task: Task) => {
    if (!session?.user?.id) return;

    try {
      const updatedTask = await apiClient.updateTask(session.user.id, task.id, {
        title: task.title,
        description: task.description,
        completed: task.completed,
      });
      setTasks(prev => prev.map(t => t.id === updatedTask.id ? updatedTask : t));
    } catch (err) {
      setError('Failed to update task');
      console.error('Error updating task:', err);
    }
  };

  const handleTaskDelete = async (taskId: string) => {
    if (!session?.user?.id) return;

    try {
      await apiClient.deleteTask(session.user.id, taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (err) {
      setError('Failed to delete task');
      console.error('Error deleting task:', err);
    }
  };

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Not Authenticated</h2>
          <p className="text-gray-600">Please sign in to access your tasks.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
              <p className="text-gray-600">Manage your todo list</p>
            </div>
            <button
              onClick={() => router.push('/tasks/new')}
              className="btn-primary"
            >
              Add Task
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Task List */}
        <div className="card p-6">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600">{error}</p>
              <button
                onClick={fetchTasks}
                className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
              >
                Retry
              </button>
            </div>
          )}

          <TaskList
            userId={session.user.id}
            tasks={tasks}
            onTaskUpdate={handleTaskUpdate}
            onTaskDelete={handleTaskDelete}
            loading={loading}
            error={error}
          />

          {/* Footer Actions */}
          <div className="mt-6 flex justify-end space-x-3">
            <button
              onClick={() => router.push('/tasks/new')}
              className="btn-primary"
            >
              Add Task
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}