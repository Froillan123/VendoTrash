import React, { createContext, useContext, useState, useCallback } from 'react';
import { User, currentUser, mockUsers } from '@/lib/mockData';

interface AuthContextType {
  user: User | null;
  isAdmin: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string, asAdmin?: boolean) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  updateUserPoints: (points: number) => void;
  updateUserStats: (trashType: 'PLASTIC' | 'METAL') => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);

  const login = useCallback(async (email: string, password: string, asAdmin = false): Promise<boolean> => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    if (asAdmin) {
      if (email === 'admin@vendotrash.com' && password === 'admin123') {
        setIsAdmin(true);
        setUser({ ...currentUser, name: 'Admin User', email: 'admin@vendotrash.com' });
        return true;
      }
      return false;
    }
    
    const foundUser = mockUsers.find(u => u.email === email);
    if (foundUser || (email && password)) {
      setUser(foundUser || { ...currentUser, email });
      setIsAdmin(false);
      return true;
    }
    return false;
  }, []);

  const register = useCallback(async (name: string, email: string, password: string): Promise<boolean> => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    if (name && email && password) {
      const newUser: User = {
        id: String(Date.now()),
        name,
        email,
        totalPoints: 0,
        totalPlastic: 0,
        totalMetal: 0,
        totalTransactions: 0,
        status: 'Active',
        createdAt: new Date().toISOString().split('T')[0],
      };
      setUser(newUser);
      setIsAdmin(false);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setIsAdmin(false);
  }, []);

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
  }, []);

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
