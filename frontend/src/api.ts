import axios from 'axios';

const API_URL = '/api';

const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect if we're already on the login page or if it's a login request
    const isLoginRequest = error.config?.url?.includes('/login');
    const isOnLoginPage = window.location.pathname === '/login';
    
    if (error.response?.status === 401 && !isLoginRequest && !isOnLoginPage) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Employee {
  id: number;
  name: string;
  salary: number;
}

export interface PayrollRun {
  id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  completed_at: string | null;
}

export const authApi = {
  login: async (data: LoginRequest) => {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response = await api.post('/login', formData);
    return response.data;
  },
};

export const employeeApi = {
  getAll: async (): Promise<Employee[]> => {
    const response = await api.get('/employees');
    return response.data;
  },
};

export const payrollApi = {
  runPayroll: async (employeeIds: number[]): Promise<PayrollRun> => {
    const response = await api.post('/payroll/run', { employee_ids: employeeIds });
    return response.data;
  },
  
  getStatus: async (runId: number): Promise<PayrollRun> => {
    const response = await api.get(`/payroll/${runId}`);
    return response.data;
  },
  
  downloadPdf: (runId: number): string => {
    return `/api/payroll/${runId}/pdf`;
  },
};

export default api;