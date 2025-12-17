import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { authAPI, usersAPI, vendoAPI, User as APIUser, setAuthToken, removeAuthToken } from '@/lib/api';

// Map API User to Client User format
interface User {
  id: string;
  name: string;
  email: string;
  totalPoints: number;
  totalPlastic: number;
  totalMetal: number;
  totalTransactions: number;
  status: 'Active' | 'Inactive';
  createdAt: string;
}

interface AuthContextType {
  user: User | null;
  isAdmin: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, asAdmin?: boolean) => Promise<boolean>;
  register: (name: string, email: string, password: string, isAdmin?: boolean) => Promise<boolean>;
  logout: () => void;
  updateUserPoints: (points: number) => void;
  updateUserStats: (trashType: 'PLASTIC' | 'METAL') => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper to convert API User to Client User
const mapAPIUserToClient = (apiUser: APIUser): User => {
  return {
    id: String(apiUser.id),
    name: apiUser.username,
    email: apiUser.email,
    totalPoints: apiUser.total_points,
    totalPlastic: apiUser.total_plastic,
    totalMetal: apiUser.total_metal,
    totalTransactions: apiUser.total_transactions,
    status: apiUser.is_active ? 'Active' : 'Inactive',
    createdAt: apiUser.created_at.split('T')[0],
  };
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);

  // Helper to decode JWT token and get user ID
  const getUserIdFromToken = (token: string): number | null => {
    try {
      // JWT token format: header.payload.signature
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      return decoded.sub || null; // 'sub' is the user ID in JWT
    } catch {
      return null;
    }
  };

  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('auth_token');
      
      if (token && !token.startsWith('temp_')) {
        try {
          // Try to get current user using /me endpoint
          const apiUser = await usersAPI.getMe();
          setUser(mapAPIUserToClient(apiUser));
          setIsAdmin(apiUser.role === 'admin');
        } catch (error) {
          // Token invalid or expired, clear storage
          removeAuthToken();
        }
      }
    };
    
    loadUser();
  }, []);

  const login = useCallback(async (email: string, password: string, asAdmin = false): Promise<boolean> => {
    try {
      const response = await authAPI.login({ email, password });
    
      if (response.user) {
      const clientUser = mapAPIUserToClient(response.user);
      setUser(clientUser);
      setIsAdmin(response.user?.role === 'admin' || false);
      
      // Store JWT token from login response
      if (response.access_token) {
        setAuthToken(response.access_token);
      }
        
      return true;
    }
    return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  }, []);

  const register = useCallback(async (name: string, email: string, password: string, isAdminAccount = false): Promise<boolean> => {
    try {
      let response;
      
      if (isAdminAccount) {
        // Use admin registration endpoint
        response = await usersAPI.createAdmin({
          username: name,
          email,
          password,
        });
      } else {
        // Use regular registration endpoint
        response = await authAPI.register({
          username: name,
          email,
          password,
        });
      }
      
      // Registration now returns token and user (auto-login)
      if (response.access_token && response.user) {
        const clientUser = mapAPIUserToClient(response.user);
        setUser(clientUser);
        setIsAdmin(response.user.role === 'admin' || false);
        
        // Store JWT token for auto-login - MUST be synchronous
        setAuthToken(response.access_token);
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Register error:', error);
      throw error; // Re-throw to be caught by UI
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      // Clear token on server (for Arduino bridge)
      try {
        await vendoAPI.clearToken();
      } catch (error) {
        // Continue even if token clearing fails
        console.error('Token cleanup error:', error);
      }
      
      // Call server-side logout endpoint
      await authAPI.logout();
    } catch (error) {
      // Even if server logout fails, continue with client-side logout
      console.error('Logout error:', error);
    } finally {
      // Always clear client-side state
      setUser(null);
      setIsAdmin(false);
      removeAuthToken(); // This already removes from localStorage
      // Clear any cached data
      localStorage.removeItem('auth_token');
    }
  }, []);

  const refreshUser = useCallback(async () => {
    if (!user) return;
    
    try {
      const apiUser = await usersAPI.getById(Number(user.id));
      setUser(mapAPIUserToClient(apiUser));
    } catch (error) {
      console.error('Refresh user error:', error);
    }
  }, [user]);

  const updateUserPoints = useCallback((points: number) => {
    setUser(prev => prev ? { ...prev, totalPoints: prev.totalPoints + points } : null);
  }, []);

  const updateUserStats = useCallback((trashType: 'PLASTIC' | 'METAL') => {
    setUser(prev => {
      if (!prev) return null;
      const points = trashType === 'PLASTIC' ? 2 : 1;
      return {
        ...prev,
        totalPoints: prev.totalPoints + points,
        totalPlastic: trashType === 'PLASTIC' ? prev.totalPlastic + 1 : prev.totalPlastic,
        totalMetal: trashType === 'METAL' ? prev.totalMetal + 1 : prev.totalMetal,
        totalTransactions: prev.totalTransactions + 1,
      };
    });
    
    // Refresh from server after a short delay
    setTimeout(() => {
      refreshUser();
    }, 1000);
  }, [refreshUser]);

  return (
    <AuthContext.Provider value={{
      user,
      isAdmin,
      isAuthenticated: !!user,
      login,
      register,
      logout,
      updateUserPoints,
      updateUserStats,
      refreshUser,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
