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
import { mockTransactions, Transaction } from '@/lib/mockData';

type MachineStatus = 'Idle' | 'Ready' | 'Detecting' | 'Completed';

const Dashboard = () => {
  const { user, updateUserStats } = useAuth();
  const { toast } = useToast();
  const [machineStatus, setMachineStatus] = useState<MachineStatus>('Idle');
  const [lastDetection, setLastDetection] = useState<{ type: 'PLASTIC' | 'METAL'; points: number } | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>(mockTransactions.filter(t => t.userId === '1').slice(0, 5));

  const handleInsertTrash = async () => {
    if (machineStatus !== 'Idle') return;

    // Start the detection process
    setMachineStatus('Ready');
    
    setTimeout(() => {
      setMachineStatus('Detecting');
    }, 1000);

    setTimeout(() => {
      // Randomly determine trash type
      const trashType = Math.random() > 0.4 ? 'PLASTIC' : 'METAL';
      const points = trashType === 'PLASTIC' ? 2 : 1;
      
      setLastDetection({ type: trashType, points });
      setMachineStatus('Completed');
      updateUserStats(trashType);

      // Add new transaction
      const newTransaction: Transaction = {
        id: `t${Date.now()}`,
        userId: user?.id || '1',
        trashType,
        pointsEarned: points,
        timestamp: new Date().toISOString(),
        status: 'Completed',
      };
      setTransactions(prev => [newTransaction, ...prev.slice(0, 4)]);

      toast({
        title: `${trashType} Detected!`,
        description: `You earned ${points} point${points > 1 ? 's' : ''}`,
      });

      // Reset after 3 seconds
      setTimeout(() => {
        setMachineStatus('Idle');
      }, 3000);
    }, 2500);
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
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Welcome Section */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Welcome back, {user?.name?.split(' ')[0]}!
          </h1>
          <p className="text-muted-foreground flex items-center gap-2">
            <Leaf className="h-4 w-4 text-primary" />
            Keep recycling for a better tomorrow
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '0ms' }}>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-primary/10">
                <Coins className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{user?.totalPoints || 0}</p>
                <p className="text-xs text-muted-foreground">Total Points</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '50ms' }}>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-blue-500/10">
                <Recycle className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{user?.totalPlastic || 0}</p>
                <p className="text-xs text-muted-foreground">Plastic Items</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-amber-500/10">
                <Zap className="h-5 w-5 text-amber-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{user?.totalMetal || 0}</p>
                <p className="text-xs text-muted-foreground">Metal Items</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '150ms' }}>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-accent/10">
                <TrendingUp className="h-5 w-5 text-accent" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{user?.totalTransactions || 0}</p>
                <p className="text-xs text-muted-foreground">Transactions</p>
              </div>
            </div>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
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
            <CardContent className="space-y-6">
              {/* Machine Status */}
              <div className="flex items-center justify-between p-4 rounded-lg bg-secondary/50">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
                  <span className="font-medium text-foreground">Machine Status:</span>
                </div>
                <Badge variant={machineStatus === 'Idle' ? 'secondary' : 'default'}>
                  {machineStatus}
                </Badge>
              </div>

              {/* Insert Button */}
              <Button
                onClick={handleInsertTrash}
                disabled={machineStatus !== 'Idle'}
                variant="eco"
                size="xl"
                className="w-full"
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
                <div className={`p-4 rounded-lg border-2 ${
                  lastDetection.type === 'PLASTIC' 
                    ? 'bg-blue-50 border-blue-200' 
                    : 'bg-amber-50 border-amber-200'
                } animate-scale-in`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Latest Detection</p>
                      <p className={`text-lg font-bold ${
                        lastDetection.type === 'PLASTIC' ? 'text-blue-600' : 'text-amber-600'
                      }`}>
                        {lastDetection.type}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Points Earned</p>
                      <p className="text-lg font-bold text-primary">+{lastDetection.points}</p>
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
              <div className="space-y-3">
                {transactions.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No transactions yet. Start recycling!
                  </p>
                ) : (
                  transactions.map((tx, index) => (
                    <div 
                      key={tx.id} 
                      className="flex items-center justify-between p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${
                          tx.trashType === 'PLASTIC' 
                            ? 'bg-blue-500/10' 
                            : 'bg-amber-500/10'
                        }`}>
                          <Recycle className={`h-4 w-4 ${
                            tx.trashType === 'PLASTIC' 
                              ? 'text-blue-500' 
                              : 'text-amber-500'
                          }`} />
                        </div>
                        <div>
                          <p className="font-medium text-foreground">{tx.trashType}</p>
                          <p className="text-xs text-muted-foreground">{formatDate(tx.timestamp)}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-primary">+{tx.pointsEarned}</p>
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
