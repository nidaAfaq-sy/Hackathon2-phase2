export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  completed?: boolean;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface TaskFilter {
  completed?: boolean;
  search?: string;
}

export interface TaskListResponse {
  tasks: Task[];
}

export interface ErrorResponse {
  error: string;
  message: string;
}

export interface AuthCredentials {
  email: string;
  password: string;
}