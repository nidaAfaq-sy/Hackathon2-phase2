'use client';

import { useSession } from '../lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiClient } from '../lib/api';
import { Task } from '../lib/types';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Dashboard() {
  const { data: session, isPending } = useSession();
  const status = isPending ? 'loading' : session ? 'authenticated' : 'unauthenticated';
  const router = useRouter();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === 'loading') return;

    // If no session, stop loading
    if (!session) {
      setLoading(false);
      return;
    }

    // If we have a session, fetch tasks
    if (session) {
      fetchTasks();
    }
  }, [session, status]);

  const fetchTasks = async () => {
    if (!session?.user?.id) return;

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.getTasks(session.user.id);
      setTasks(response.tasks);
    } catch (err) {
      setError('Failed to load tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      // Trigger storage event to update session
      window.dispatchEvent(new Event('storage'));
      router.push('/auth/signin');
    }
  };

  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks(prev => prev.map(task => task.id === updatedTask.id ? updatedTask : task));
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
          <p className="text-gray-600 mb-6">Please sign in to access your tasks.</p>
          <button
            onClick={() => router.push('/auth/signin')}
            className="btn-primary"
          >
            Sign In
          </button>
        </div>
      </div>
    );
  }

  const completedTasks = tasks.filter(task => task.completed).length;
  const pendingTasks = tasks.filter(task => !task.completed).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Welcome back, {session.user.email}!
              </h1>
              <p className="text-gray-600">Your task management dashboard</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => router.push('/tasks/new')}
                className="btn-primary"
              >
                Create Task
              </button>
              <button
                onClick={() => router.push('/tasks')}
                className="btn-secondary"
              >
                View All Tasks
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Tasks</h3>
            <p className="text-3xl font-bold text-blue-600">{tasks.length}</p>
          </div>
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Completed</h3>
            <p className="text-3xl font-bold text-green-600">{completedTasks}</p>
          </div>
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Pending</h3>
            <p className="text-3xl font-bold text-yellow-600">{pendingTasks}</p>
          </div>
        </div>

        {/* Recent Activity */}
        {tasks.length > 0 && (
          <div className="card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-4">
              {tasks.slice(0, 5).map(task => (
                <div key={task.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className={`font-medium ${
                      task.completed ? 'text-gray-500 line-through' : 'text-gray-900'
                    }`}>
                      {task.title}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Created: {new Date(task.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex space-x-2">
                    <span className={`chip ${
                      task.completed
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {task.completed ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            {tasks.length > 5 && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => router.push('/tasks')}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  View All Tasks →
                </button>
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {tasks.length === 0 && !loading && (
          <div className="card p-8 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No tasks yet</h2>
            <p className="text-gray-600 mb-6">Create your first task to get started</p>
            <button
              onClick={() => router.push('/tasks/new')}
              className="btn-primary"
            >
              Create Your First Task
            </button>
          </div>
        )}
      </main>
    </div>
  );
}