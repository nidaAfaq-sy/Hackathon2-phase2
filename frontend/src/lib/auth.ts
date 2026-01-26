// Custom JWT-based session management
import { useState, useEffect } from 'react';
import axios from 'axios';

interface User {
  id: string;
  email: string;
}

interface Session {
  user: User;
}

interface UseSessionResult {
  data: Session | null;
  isPending: boolean;
  error: Error | null;
  refetch: () => void;
}

// Decode JWT token (client-side only, for display purposes)
function decodeJWT(token: string): { user_id?: string; email?: string } | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

// Custom useSession hook that works with JWT in localStorage
export function useSession(): UseSessionResult {
  const [data, setData] = useState<Session | null>(null);
  const [isPending, setIsPending] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Guard against SSR - localStorage is only available in browser
    if (typeof window === 'undefined') {
      setIsPending(false);
      return;
    }
    
    const checkSession = () => {
      setIsPending(true);
      setError(null);
      
      try {
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          setData(null);
          setIsPending(false);
          return;
        }

        // Decode JWT to get user info
        const payload = decodeJWT(token);
        
        if (payload && payload.user_id && payload.email) {
          setData({
            user: {
              id: payload.user_id,
              email: payload.email,
            },
          });
          setIsPending(false);
        } else {
          // Invalid token format, clear it
          localStorage.removeItem('auth_token');
          setData(null);
          setIsPending(false);
        }
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to read session'));
        setData(null);
        setIsPending(false);
      }
    };

    // Initial check
    checkSession();
    
    // Listen for storage changes (e.g., when token is set/removed in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth_token') {
        checkSession();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const refetch = () => {
    if (typeof window === 'undefined') return;
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setData(null);
      setIsPending(false);
      return;
    }
    try {
      const payload = decodeJWT(token);
      if (payload && payload.user_id && payload.email) {
        setData({
          user: {
            id: payload.user_id,
            email: payload.email,
          },
        });
        setIsPending(false);
      } else {
        localStorage.removeItem('auth_token');
        setData(null);
        setIsPending(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to read session'));
      setData(null);
      setIsPending(false);
    }
  };

  return {
    data,
    isPending,
    error,
    refetch,
  };
}

// Keep authClient for backward compatibility (it was axios-based)
export const authClient = {
  useSession,
};

// Create axios instance for API calls with JWT token handling
export const apiAxiosClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
apiAxiosClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage (you can change this to your preferred storage)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
apiAxiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access - clear token but don't redirect
      // The component's useSession hook will handle the UI state
      localStorage.removeItem('auth_token');
      // Trigger a storage event so useSession can detect the change
      window.dispatchEvent(new Event('storage'));
    }
    return Promise.reject(error);
  }
);

export default authClient;