import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Leaf, 
  Recycle, 
  Coins, 
  TrendingUp, 
  Play,
  CheckCircle,
  Loader,
  Zap
} from 'lucide-react';
import { transactionsAPI, vendoAPI, Transaction } from '@/lib/api';

type MachineStatus = 'Idle' | 'Ready' | 'Detecting' | 'Completed';

const Dashboard = () => {
  const { user, updateUserStats, refreshUser, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [machineStatus, setMachineStatus] = useState<MachineStatus>('Idle');
  const [lastDetection, setLastDetection] = useState<{ type: 'PLASTIC' | 'NON_PLASTIC'; points: number } | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load transactions on mount - wait for user to be authenticated
  useEffect(() => {
    if (user && isAuthenticated) {
      loadTransactions();
    }
  }, [user, isAuthenticated]);

  const loadTransactions = async () => {
    if (!user) return;
    
    try {
      const response = await transactionsAPI.getByUser(0, 5);
      // Handle paginated response
      const transactionsList = Array.isArray(response) ? response : (response.items || []);
      setTransactions(transactionsList);
    } catch (error) {
      console.error('Error loading transactions:', error);
    }
  };

  const handleInsertTrash = async () => {
    if (machineStatus !== 'Idle' || !user || isLoading) return;

    setIsLoading(true);
    setMachineStatus('Ready');
    
    try {
      // Step 1: Send command to ESP32/Arduino
      setTimeout(async () => {
        setMachineStatus('Detecting');
        
        try {
          // For demo, we'll determine material type (in real app, this comes from computer vision)
          // You can modify this to call computer vision API first
          const materialType = Math.random() > 0.4 ? 'PLASTIC' : 'NON_PLASTIC';
          const points = materialType === 'PLASTIC' ? 2 : 1;
          
          // Send command to ESP32
          await vendoAPI.sendCommand(materialType);
          
          // Create transaction in database
          // Note: user_id comes from JWT token automatically
          // machine_id should be configurable - using 1 as default
          const newTransaction = await transactionsAPI.create({
            machine_id: 1, // Default machine - should be configurable
            material_type: materialType,
            points_earned: points,
          });
          
          setLastDetection({ type: materialType, points });
          setMachineStatus('Completed');
          
          // Update local state
          updateUserStats(materialType === 'PLASTIC' ? 'PLASTIC' : 'METAL');
          
          // Reload transactions
          await loadTransactions();
          
          // Refresh user data from server
          await refreshUser();
          
          toast({
            title: `${materialType === 'PLASTIC' ? 'PLASTIC' : 'NON-PLASTIC'} Detected!`,
            description: `You earned ${points} point${points > 1 ? 's' : ''}`,
          });
          
          // Reset after 3 seconds
          setTimeout(() => {
            setMachineStatus('Idle');
            setIsLoading(false);
          }, 3000);
        } catch (error: any) {
          console.error('Error processing trash:', error);
          toast({
            title: 'Error',
            description: error.message || 'Failed to process trash',
            variant: 'destructive',
          });
          setMachineStatus('Idle');
          setIsLoading(false);
        }
      }, 1000);
    } catch (error: any) {
      console.error('Error:', error);
      setMachineStatus('Idle');
      setIsLoading(false);
    }
  };

  const getStatusColor = () => {
    switch (machineStatus) {
      case 'Ready': return 'bg-yellow-500';
      case 'Detecting': return 'bg-blue-500 animate-pulse';
      case 'Completed': return 'bg-green-500';
      default: return 'bg-muted-foreground';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Welcome Section */}
        <div className="mb-6 sm:mb-8 lg:mb-10 animate-fade-in">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-2">
            Welcome back, {user?.name || 'Recycler'}!
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground flex items-center gap-2">
            <Leaf className="h-4 w-4 text-primary" />
            Keep recycling for a better tomorrow
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-5 mb-6 sm:mb-8">
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '0ms' }}>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="p-2 sm:p-2.5 rounded-lg bg-primary/10 flex-shrink-0">
                <Coins className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground truncate">{user?.totalPoints || 0}</p>
                <p className="text-xs sm:text-sm text-muted-foreground">Total Points</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '50ms' }}>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="p-2 sm:p-2.5 rounded-lg bg-blue-500/10 flex-shrink-0">
                <Recycle className="h-4 w-4 sm:h-5 sm:w-5 text-blue-500" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground truncate">{user?.totalPlastic || 0}</p>
                <p className="text-xs sm:text-sm text-muted-foreground">Plastic Items</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="p-2 sm:p-2.5 rounded-lg bg-amber-500/10 flex-shrink-0">
                <Zap className="h-4 w-4 sm:h-5 sm:w-5 text-amber-500" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground truncate">{user?.totalMetal || 0}</p>
                <p className="text-xs sm:text-sm text-muted-foreground">Non-Plastic</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '150ms' }}>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="p-2 sm:p-2.5 rounded-lg bg-accent/10 flex-shrink-0">
                <TrendingUp className="h-4 w-4 sm:h-5 sm:w-5 text-accent" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground truncate">{user?.totalTransactions || 0}</p>
                <p className="text-xs sm:text-sm text-muted-foreground">Transactions</p>
              </div>
            </div>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-4 sm:gap-5 lg:gap-6">
          {/* Insert Trash Section */}
          <Card className="shadow-card animate-slide-up" style={{ animationDelay: '200ms' }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Recycle className="h-5 w-5 text-primary" />
                Insert Trash
              </CardTitle>
              <CardDescription>
                Deposit your recyclable items to earn points
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 sm:space-y-6">
              {/* Machine Status */}
              <div className="flex items-center justify-between p-3 sm:p-4 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className={`w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full ${getStatusColor()}`} />
                  <span className="text-sm sm:text-base font-medium text-foreground">Machine Status:</span>
                </div>
                <Badge variant={machineStatus === 'Idle' ? 'secondary' : 'default'} className="text-xs sm:text-sm">
                  {machineStatus}
                </Badge>
              </div>

              {/* Insert Button */}
              <Button
                onClick={handleInsertTrash}
                disabled={machineStatus !== 'Idle' || isLoading}
                variant="eco"
                size="lg"
                className="w-full h-12 sm:h-14 text-base sm:text-lg"
              >
                {machineStatus === 'Idle' && (
                  <>
                    <Play className="h-5 w-5" />
                    Insert Trash
                  </>
                )}
                {machineStatus === 'Ready' && (
                  <>
                    <Loader className="h-5 w-5 animate-spin" />
                    Preparing...
                  </>
                )}
                {machineStatus === 'Detecting' && (
                  <>
                    <Loader className="h-5 w-5 animate-spin" />
                    Detecting...
                  </>
                )}
                {machineStatus === 'Completed' && (
                  <>
                    <CheckCircle className="h-5 w-5" />
                    Detection Complete!
                  </>
                )}
              </Button>

              {/* Last Detection Result */}
              {lastDetection && (
                <div className={`p-3 sm:p-4 rounded-lg border-2 ${
                  lastDetection.type === 'PLASTIC' 
                    ? 'bg-blue-50 border-blue-200 dark:bg-blue-950/20 dark:border-blue-800' 
                    : 'bg-amber-50 border-amber-200 dark:bg-amber-950/20 dark:border-amber-800'
                } animate-scale-in`}>
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">Latest Detection</p>
                      <p className={`text-base sm:text-lg font-bold ${
                        lastDetection.type === 'PLASTIC' ? 'text-blue-600' : 'text-amber-600'
                      }`}>
                        {lastDetection.type === 'PLASTIC' ? 'PLASTIC' : 'NON-PLASTIC'}
                      </p>
                    </div>
                    <div className="text-left sm:text-right">
                      <p className="text-xs sm:text-sm text-muted-foreground">Points Earned</p>
                      <p className="text-base sm:text-lg font-bold text-primary">+{lastDetection.points}</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Transaction History */}
          <Card className="shadow-card animate-slide-up" style={{ animationDelay: '250ms' }}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Recent Transactions
              </CardTitle>
              <CardDescription>
                Your latest recycling activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 sm:space-y-3">
                {transactions.length === 0 ? (
                  <p className="text-center text-sm sm:text-base text-muted-foreground py-8">
                    No transactions yet. Start recycling!
                  </p>
                ) : (
                  transactions.map((tx, index) => (
                    <div 
                      key={tx.id} 
                      className="flex items-center justify-between p-3 sm:p-4 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
                        <div className={`p-1.5 sm:p-2 rounded-lg flex-shrink-0 ${
                          tx.material_type === 'PLASTIC' 
                            ? 'bg-blue-500/10' 
                            : 'bg-amber-500/10'
                        }`}>
                          <Recycle className={`h-3.5 w-3.5 sm:h-4 sm:w-4 ${
                            tx.material_type === 'PLASTIC' 
                              ? 'text-blue-500' 
                              : 'text-amber-500'
                          }`} />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm sm:text-base font-medium text-foreground truncate">
                            {tx.material_type === 'PLASTIC' ? 'PLASTIC' : 'NON-PLASTIC'}
                          </p>
                          <p className="text-xs text-muted-foreground">{formatDate(tx.created_at)}</p>
                        </div>
                      </div>
                      <div className="text-right flex-shrink-0 ml-2">
                        <p className="text-sm sm:text-base font-semibold text-primary">+{tx.points_earned}</p>
                        <Badge variant="secondary" className="text-xs">{tx.status}</Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Dashboard;
