'use client';

import { useSession } from '../../../lib/auth';
import { useRouter, useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiClient } from '../../../lib/api';
import { Task, TaskUpdate } from '../../../lib/types';
import TaskForm from '../../../components/TaskForm';
import LoadingSpinner from '../../../components/LoadingSpinner';

export default function EditTaskPage() {
  const { data: session, isPending } = useSession();
  const status = isPending ? 'loading' : session ? 'authenticated' : 'unauthenticated';
  const router = useRouter();
  const params = useParams();
  const taskId = params.id as string;

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === 'loading') return;

    if (session) {
      fetchTask();
    }
  }, [session, status, taskId]);

  const fetchTask = async () => {
    if (!session?.user?.id) return;

    setLoading(true);
    setError(null);

    try {
      const fetchedTask = await apiClient.getTask(session.user.id, taskId);
      setTask(fetchedTask);
    } catch (err) {
      setError('Failed to load task');
      console.error('Error fetching task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (taskData: TaskUpdate) => {
    if (!session?.user?.id || !task) return;

    setLoading(true);
    setError(null);

    try {
      const updatedTask = await apiClient.updateTask(session.user.id, task.id, taskData);
      router.push('/tasks');
    } catch (err) {
      setError('Failed to update task');
      console.error('Error updating task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/tasks');
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
          <p className="text-gray-600">Please sign in to edit tasks.</p>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Task Not Found</h2>
          <p className="text-gray-600 mb-6">The task you're looking for doesn't exist or you don't have permission to access it.</p>
          <button
            onClick={() => router.push('/tasks')}
            className="btn-primary"
          >
            Back to Tasks
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Edit Task</h1>
              <p className="text-gray-600">Update the details for "{task.title}"</p>
            </div>
            <button
              onClick={() => router.push('/tasks')}
              className="btn-secondary"
            >
              Back to Tasks
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card p-6">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          <TaskForm
            task={task}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            loading={loading}
          />
        </div>
      </main>
    </div>
  );
}