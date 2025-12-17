import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Leaf, LogIn, Mail, Lock, Recycle } from 'lucide-react';
import logo from '@/assets/logo.png';

const Login = () => {
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
    const success = await login(email, password);
    setIsLoading(false);

    if (success) {
      toast({
        title: 'Welcome back!',
        description: 'Successfully logged in to VendoTrash',
      });
      navigate('/dashboard');
    } else {
      toast({
        title: 'Login Failed',
        description: 'Invalid email or password',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Decorative Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent/5 rounded-full blur-3xl" />
      </div>

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md animate-fade-in">
          {/* Logo Section */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <img src={logo} alt="VendoTrash" className="h-20 w-auto" />
            </div>
            <h1 className="text-2xl font-bold text-foreground mb-2">Welcome to VendoTrash</h1>
            <p className="text-muted-foreground flex items-center justify-center gap-2">
              <Recycle className="h-4 w-4 text-primary" />
              Smart Recycling, Real Rewards
            </p>
          </div>

          {/* Login Card */}
          <Card className="shadow-card border-border/50">
            <CardHeader className="space-y-1 pb-4">
              <CardTitle className="text-xl flex items-center gap-2">
                <LogIn className="h-5 w-5 text-primary" />
                User Login
              </CardTitle>
              <CardDescription>
                Enter your credentials to access your account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email" className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
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
                      Logging in...
                    </span>
                  ) : (
                    <>
                      <LogIn className="h-4 w-4" />
                      Login
                    </>
                  )}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Don't have an account?{' '}
                  <Link to="/register" className="text-primary hover:underline font-medium">
                    Register here
                  </Link>
                </p>
              </div>

              <div className="mt-4 pt-4 border-t border-border">
                <Link to="/admin/login">
                  <Button variant="ghost" size="sm" className="w-full text-muted-foreground">
                    <Leaf className="h-4 w-4 mr-2" />
                    Admin Login
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Demo Credentials */}
          <div className="mt-4 p-4 rounded-lg bg-secondary/50 border border-border/50">
            <p className="text-xs text-center text-muted-foreground">
              <strong>Demo:</strong> Use any email and password to login
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
