import { Task, TaskCreate, TaskUpdate, TaskFilter, TaskListResponse } from './types';
import { apiAxiosClient } from './auth';

class ApiClient {
  // Task methods
  async getTasks(userId: string, filter?: TaskFilter): Promise<TaskListResponse> {
    let url = `/users/${userId}/tasks`;
    if (filter) {
      const params = new URLSearchParams();
      if (filter.completed !== undefined) params.append('completed', filter.completed.toString());
      if (filter.search) params.append('search', filter.search);
      url += `?${params.toString()}`;
    }
    const response = await apiAxiosClient.get(url);
    return response.data;
  }

  async createTask(userId: string, taskData: TaskCreate): Promise<Task> {
    const response = await apiAxiosClient.post(`/users/${userId}/tasks`, taskData);
    return response.data;
  }

  async getTask(userId: string, taskId: string): Promise<Task> {
    const response = await apiAxiosClient.get(`/users/${userId}/tasks/${taskId}`);
    return response.data;
  }

  async updateTask(userId: string, taskId: string, taskData: TaskUpdate): Promise<Task> {
    const response = await apiAxiosClient.put(`/users/${userId}/tasks/${taskId}`, taskData);
    return response.data;
  }

  async deleteTask(userId: string, taskId: string): Promise<void> {
    await apiAxiosClient.delete(`/users/${userId}/tasks/${taskId}`);
  }

  // Auth methods
  async login(credentials: { email: string; password: string }): Promise<any> {
    const response = await apiAxiosClient.post('/auth/signin', credentials);
    return response.data;
  }

  async register(credentials: { email: string; password: string }): Promise<any> {
    const response = await apiAxiosClient.post('/auth/signup', credentials);
    return response.data;
  }

  async getCurrentUser(): Promise<any> {
    const response = await apiAxiosClient.get('/auth/me');
    return response.data;
  }
}

export const apiClient = new ApiClient();