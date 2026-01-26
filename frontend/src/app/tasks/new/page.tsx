'use client';

import { useSession } from '../../../lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiClient } from '../../../lib/api';
import { TaskCreate } from '../../../lib/types';
import TaskForm from '../../../components/TaskForm';
import LoadingSpinner from '../../../components/LoadingSpinner';

export default function CreateTaskPage() {
  const { data: session, isPending } = useSession();
  const status = isPending ? 'loading' : session ? 'authenticated' : 'unauthenticated';
  const router = useRouter();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Session check is handled in render

  const handleSubmit = async (taskData: TaskCreate) => {
    if (!session?.user?.id) return;

    setLoading(true);
    setError(null);

    try {
      await apiClient.createTask(session.user.id, taskData);
      router.push('/tasks');
    } catch (err) {
      setError('Failed to create task');
      console.error('Error creating task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/tasks');
  };

  if (status === 'loading') {
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
          <p className="text-gray-600">Please sign in to create tasks.</p>
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
              <h1 className="text-2xl font-bold text-gray-900">Create New Task</h1>
              <p className="text-gray-600">Fill in the details for your new task</p>
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
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            loading={loading}
          />
        </div>
      </main>
    </div>
  );
}