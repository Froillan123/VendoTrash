import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Shield, LogIn, Mail, Lock, UserPlus } from 'lucide-react';
import logo from '@/assets/logo.png';

const AdminLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all fields',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    const success = await login(email, password, true);
    setIsLoading(false);

    if (success) {
      toast({
        title: 'Admin Access Granted',
        description: 'Welcome to the admin dashboard',
      });
      navigate('/admin');
    } else {
      toast({
        title: 'Access Denied',
        description: 'Invalid admin credentials',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Decorative Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-64 bg-gradient-to-b from-primary/5 to-transparent" />
      </div>

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md animate-fade-in">
          {/* Logo Section */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <img src={logo} alt="VendoTrash" className="h-20 w-auto" />
            </div>
            <h1 className="text-2xl font-bold text-foreground mb-2">Admin Portal</h1>
            <p className="text-muted-foreground flex items-center justify-center gap-2">
              <Shield className="h-4 w-4 text-primary" />
              VendoTrash Management System
            </p>
          </div>

          {/* Login Card */}
          <Card className="shadow-card border-border/50 border-t-4 border-t-primary">
            <CardHeader className="space-y-1 pb-4">
              <CardTitle className="text-xl flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Admin Login
              </CardTitle>
              <CardDescription>
                Enter your admin credentials to access the dashboard
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email" className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    Admin Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="admin@vendotrash.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-11"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password" className="flex items-center gap-2">
                    <Lock className="h-4 w-4 text-muted-foreground" />
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full h-11" 
                  variant="eco"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <span className="h-4 w-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                      Authenticating...
                    </span>
                  ) : (
                    <>
                      <LogIn className="h-4 w-4" />
                      Access Dashboard
                    </>
                  )}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground mb-3">
                  Don't have an admin account?{' '}
                  <Link to="/admin/register" className="text-primary hover:underline font-medium">
                    Create Admin Account
                  </Link>
                </p>
                <Link to="/login">
                  <Button variant="ghost" size="sm" className="text-muted-foreground">
                    ← Back to User Login
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Demo Credentials */}
          <div className="mt-4 p-4 rounded-lg bg-secondary/50 border border-border/50">
            <p className="text-xs text-center text-muted-foreground">
              <strong>Demo Admin:</strong> admin@vendotrash.com / admin123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;
