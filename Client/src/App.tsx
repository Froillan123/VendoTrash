import React from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";

// Pages
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Wallet from "./pages/Wallet";
import Transactions from "./pages/Transactions";
import Redeem from "./pages/Redeem";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminTransactions from "./pages/admin/AdminTransactions";
import AdminMachines from "./pages/admin/AdminMachines";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Protected Route Component (must be inside AuthProvider)
const ProtectedRoute = ({ children, adminOnly = false }: { children: React.ReactNode; adminOnly?: boolean }) => {
  try {
    const { isAuthenticated, isAdmin } = useAuth();

    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }

    if (adminOnly && !isAdmin) {
      return <Navigate to="/dashboard" replace />;
    }

    return <>{children}</>;
  } catch (error) {
    // Fallback if AuthProvider is not ready
    console.error("AuthProvider not ready:", error);
    return <Navigate to="/login" replace />;
  }
};

// Public Route (redirects if authenticated) - must be inside AuthProvider
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  try {
    const { isAuthenticated, isAdmin } = useAuth();

    if (isAuthenticated) {
      return <Navigate to={isAdmin ? "/admin" : "/dashboard"} replace />;
    }

    return <>{children}</>;
  } catch (error) {
    // If AuthProvider not ready, show public content
    console.error("AuthProvider not ready:", error);
    return <>{children}</>;
  }
};

// AppRoutes component - must be inside AuthProvider
const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Index />} />
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

      {/* User Protected Routes */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/wallet" element={<ProtectedRoute><Wallet /></ProtectedRoute>} />
      <Route path="/transactions" element={<ProtectedRoute><Transactions /></ProtectedRoute>} />
      <Route path="/redeem" element={<ProtectedRoute><Redeem /></ProtectedRoute>} />

      {/* Admin Protected Routes */}
      <Route path="/admin" element={<ProtectedRoute adminOnly><AdminDashboard /></ProtectedRoute>} />
      <Route path="/admin/users" element={<ProtectedRoute adminOnly><AdminUsers /></ProtectedRoute>} />
      <Route path="/admin/transactions" element={<ProtectedRoute adminOnly><AdminTransactions /></ProtectedRoute>} />
      <Route path="/admin/machines" element={<ProtectedRoute adminOnly><AdminMachines /></ProtectedRoute>} />

      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AuthProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
