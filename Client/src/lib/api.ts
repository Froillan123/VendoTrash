import { API_BASE_URL, API_ENDPOINTS } from './apiConfig';

// Types
export interface User {
  id: number;
  email: string;
  username: string;
  role: string;  // admin, customer
  total_points: number;
  total_plastic: number;
  total_metal: number;
  total_transactions: number;
  is_active: boolean;
  created_at: string;
}

export interface Transaction {
  id: string; // UUID as string
  user_id: number;
  machine_id: number;
  material_type: 'PLASTIC' | 'NON_PLASTIC';
  points_earned: number;
  status: string;
  created_at: string;
}

export interface Redemption {
  id: number;
  user_id: number;
  reward_id: number;
  reward?: Reward;  // Optional reward relationship
  points_used: number;
  status: string;
  created_at: string;
}

export interface Reward {
  id: number;
  name: string;
  description: string | null;
  points_required: number;
  category: 'wifi' | 'data' | 'voucher';
  is_active: boolean;
  created_at: string;
}

export interface Machine {
  id: number;
  name: string;
  location: string;
  status: 'Online' | 'Offline' | 'Maintenance';
  last_activity: string;
  bin_capacity: number;
  total_collected: number;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  token_type: string;
  user: User | null;
}

// Helper function to get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Helper function to set auth token
export const setAuthToken = (token: string): void => {
  localStorage.setItem('auth_token', token);
};

// Helper function to remove auth token
export const removeAuthToken = (): void => {
  localStorage.removeItem('auth_token');
};

// Generic fetch wrapper
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    // Add Bearer token for all authenticated requests
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { message: `HTTP error! status: ${response.status}` };
    }
    
    // Extract detail from FastAPI error response
    const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;
    throw new Error(errorMessage);
  }

  return response.json();
}

// Auth API
export const authAPI = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return apiRequest<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  logout: async (): Promise<{ message: string; status: string }> => {
    return apiRequest<{ message: string; status: string }>(API_ENDPOINTS.AUTH.LOGOUT, {
      method: 'POST',
    });
  },

  register: async (data: RegisterRequest): Promise<LoginResponse> => {
    // Registration now returns same format as login (with token)
    return apiRequest<LoginResponse>(API_ENDPOINTS.AUTH.REGISTER, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// Users API
export const usersAPI = {
  getMe: async (): Promise<User> => {
    return apiRequest<User>(API_ENDPOINTS.USERS.ME);
  },

  getAll: async (skip = 0, limit = 20, role?: string): Promise<PaginatedResponse<User>> => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (role) {
      params.append('role', role);
    }
    return apiRequest<PaginatedResponse<User>>(`${API_ENDPOINTS.USERS.BASE}?${params.toString()}`);
  },
  
  getById: async (id: number): Promise<User> => {
    return apiRequest<User>(API_ENDPOINTS.USERS.BY_ID(id));
  },

  addPoints: async (userId: number, points: number): Promise<User> => {
    return apiRequest<User>(`${API_ENDPOINTS.USERS.BY_ID(userId)}/add-points`, {
      method: 'POST',
      body: JSON.stringify({ points }),
    });
  },

  createAdmin: async (data: RegisterRequest): Promise<LoginResponse> => {
    // Admin-only endpoint to create admin users
    return apiRequest<LoginResponse>('/api/users/admin', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// Transactions API
export const transactionsAPI = {
  create: async (data: {
    machine_id: number;
    material_type: 'PLASTIC' | 'NON_PLASTIC';
    points_earned: number;
  }): Promise<Transaction> => {
    return apiRequest<Transaction>(API_ENDPOINTS.TRANSACTIONS.BASE, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getByUser: async (skip = 0, limit = 20): Promise<PaginatedResponse<Transaction>> => {
    // User ID comes from JWT token, no need to pass it
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return apiRequest<PaginatedResponse<Transaction>>(`${API_ENDPOINTS.TRANSACTIONS.BASE}?${params.toString()}`);
  },

  getAll: async (skip = 0, limit = 20): Promise<PaginatedResponse<Transaction>> => {
    // Admin endpoint to get all transactions
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    params.append('all', 'true');
    return apiRequest<PaginatedResponse<Transaction>>(`${API_ENDPOINTS.TRANSACTIONS.BASE}?${params.toString()}`);
  },

  getById: async (id: number): Promise<Transaction> => {
    return apiRequest<Transaction>(API_ENDPOINTS.TRANSACTIONS.BY_ID(id));
  },
};

// Redemptions API
export const redemptionsAPI = {
  create: async (data: {
    reward_id: number;
    points_used: number;
  }): Promise<Redemption> => {
    return apiRequest<Redemption>(API_ENDPOINTS.REDEMPTIONS.BASE, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getByUser: async (skip = 0, limit = 20): Promise<PaginatedResponse<Redemption>> => {
    // User ID comes from JWT token
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return apiRequest<PaginatedResponse<Redemption>>(`${API_ENDPOINTS.REDEMPTIONS.BASE}?${params.toString()}`);
  },

  getAll: async (skip = 0, limit = 20): Promise<PaginatedResponse<Redemption>> => {
    // Admin endpoint to get all redemptions
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    params.append('all', 'true');
    return apiRequest<PaginatedResponse<Redemption>>(`${API_ENDPOINTS.REDEMPTIONS.BASE}?${params.toString()}`);
  },

  getById: async (id: number): Promise<Redemption> => {
    return apiRequest<Redemption>(API_ENDPOINTS.REDEMPTIONS.BY_ID(id));
  },
};

// Rewards API
export const rewardsAPI = {
  getAll: async (activeOnly = true): Promise<Reward[]> => {
    const params = new URLSearchParams();
    params.append('active_only', activeOnly.toString());
    return apiRequest<Reward[]>(`${API_ENDPOINTS.REWARDS.BASE}?${params.toString()}`);
  },

  getById: async (id: number): Promise<Reward> => {
    return apiRequest<Reward>(API_ENDPOINTS.REWARDS.BY_ID(id));
  },
};

// Machines API
export const machinesAPI = {
  getAll: async (skip = 0, limit = 20): Promise<PaginatedResponse<Machine>> => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return apiRequest<PaginatedResponse<Machine>>(`${API_ENDPOINTS.MACHINES.BASE}?${params.toString()}`);
  },

  getById: async (id: number): Promise<Machine> => {
    return apiRequest<Machine>(API_ENDPOINTS.MACHINES.BY_ID(id));
  },

  updateStatus: async (id: number, status: string): Promise<Machine> => {
    return apiRequest<Machine>(`${API_ENDPOINTS.MACHINES.UPDATE_STATUS(id)}?status=${status}`, {
      method: 'PUT',
    });
  },
};

// Vendo API
export interface VendoClassifyResponse {
  status: string;
  material_type: 'PLASTIC' | 'NON_PLASTIC';
  confidence: number;
  points_earned: number;
  transaction_id?: string;
}

export const vendoAPI = {
  sendCommand: async (material: 'PLASTIC' | 'NON_PLASTIC'): Promise<{
    status: string;
    message: string;
    material?: string;
  }> => {
    return apiRequest(API_ENDPOINTS.VENDO.COMMAND, {
      method: 'POST',
      body: JSON.stringify({ material, action: 'SORT' }),
    });
  },

  getStatus: async (): Promise<{ status: string; message?: string }> => {
    return apiRequest(API_ENDPOINTS.VENDO.STATUS);
  },

  clearToken: async (): Promise<{ status: string; message: string }> => {
    return apiRequest('/api/vendo/clear-token', {
      method: 'POST',
    });
  },

  prepareInsert: async (): Promise<{ status: string; message: string; user_id?: number; session_active?: boolean }> => {
    return apiRequest('/api/vendo/prepare-insert', {
      method: 'POST',
    });
  },

  endSession: async (): Promise<{ status: string; message: string; user_id?: number }> => {
    return apiRequest('/api/vendo/end-session', {
      method: 'POST',
    });
  },

  getDetectionHistory: async (): Promise<{ status: string; history: Array<{
    material_type: string;
    confidence: number;
    points_earned: number;
    timestamp: string;
    transaction_id?: string;
  }>; count: number }> => {
    return apiRequest('/api/vendo/detection-history');
  },

  getSessionStatus: async (): Promise<{ status: string; has_session: boolean; message: string }> => {
    return apiRequest('/api/vendo/session-status');
  },
};

