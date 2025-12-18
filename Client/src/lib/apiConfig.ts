// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REGISTER: '/api/users/',
  },
  
  // Users
  USERS: {
    BASE: '/api/users/',
    ME: '/api/users/me',
    BY_ID: (id: number) => `/api/users/${id}`,
  },
  
  // Transactions
  TRANSACTIONS: {
    BASE: '/api/transactions/',
    BY_ID: (id: number) => `/api/transactions/${id}`,
  },
  
  // Redemptions
  REDEMPTIONS: {
    BASE: '/api/redemptions/',
    BY_ID: (id: number) => `/api/redemptions/${id}`,
  },
  
  // Machines
  MACHINES: {
    BASE: '/api/machines/',
    BY_ID: (id: number) => `/api/machines/${id}`,
    UPDATE_STATUS: (id: number) => `/api/machines/${id}/status`,
  },
  
  // Rewards
  REWARDS: {
    BASE: '/api/rewards/',
    BY_ID: (id: number) => `/api/rewards/${id}`,
  },
  
  // Vendo
  VENDO: {
    COMMAND: '/api/vendo/command',
    STATUS: '/api/vendo/status',
    CAPTURE_AND_CLASSIFY: '/api/vendo/capture-and-classify',
  },
};

