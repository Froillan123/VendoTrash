import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Wallet as WalletIcon, 
  Coins, 
  TrendingUp, 
  TrendingDown,
  Leaf,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { transactionsAPI, redemptionsAPI, Transaction, Redemption } from '@/lib/api';

const Wallet = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [redemptions, setRedemptions] = useState<Redemption[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [txsResponse, redsResponse] = await Promise.all([
        transactionsAPI.getByUser(0, 100),
        redemptionsAPI.getByUser(0, 100)
      ]);
      // Handle paginated responses
      setTransactions(txsResponse.items || txsResponse);
      setRedemptions(redsResponse.items || redsResponse);
    } catch (error) {
      console.error('Error loading wallet data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate stats from real data
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const pointsEarnedToday = transactions
    .filter(tx => new Date(tx.created_at) >= today && tx.points_earned > 0)
    .reduce((sum, tx) => sum + tx.points_earned, 0);
  
  const pointsRedeemed = redemptions
    .reduce((sum, r) => sum + r.points_used, 0);
  
  const remainingBalance = user?.totalPoints || 0;

  // Combine transactions and redemptions for activity feed
  const recentActivity = [
    ...transactions.slice(0, 10).map(tx => ({
      type: 'earned' as const,
      amount: tx.points_earned,
      description: `${tx.material_type === 'PLASTIC' ? 'Plastic' : 'Non-plastic'} deposit`,
      time: formatTimeAgo(tx.created_at),
    })),
    ...redemptions.slice(0, 10).map(r => ({
      type: 'redeemed' as const,
      amount: r.points_used,
      description: r.reward?.name || 'Reward redemption',
      time: formatTimeAgo(r.created_at),
    }))
  ]
    .sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
    .slice(0, 10);

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-6 sm:mb-8 lg:mb-10 animate-fade-in">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-2 flex items-center gap-2 sm:gap-3">
            <WalletIcon className="h-6 w-6 sm:h-8 sm:w-8 text-primary" />
            My Wallet
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Track your points and balance
          </p>
        </div>

        {/* Balance Card */}
        <Card className="mb-6 sm:mb-8 overflow-hidden animate-slide-up">
          <div className="eco-gradient p-6 sm:p-8 lg:p-10 text-center">
            <p className="text-primary-foreground/80 text-xs sm:text-sm mb-2">Current Balance</p>
            <div className="flex items-center justify-center gap-2 sm:gap-3 flex-wrap">
              <Coins className="h-8 w-8 sm:h-10 sm:w-10 text-primary-foreground flex-shrink-0" />
              <span className="text-4xl sm:text-5xl lg:text-6xl font-bold text-primary-foreground">
                {remainingBalance}
              </span>
              <span className="text-lg sm:text-xl text-primary-foreground/80">points</span>
            </div>
            <p className="text-primary-foreground/60 text-xs sm:text-sm mt-3 sm:mt-4">
              Keep recycling to earn more rewards!
            </p>
          </div>
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 lg:gap-5 mb-6 sm:mb-8">
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '50ms' }}>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="p-2 sm:p-2.5 rounded-lg bg-green-500/10 flex-shrink-0">
                <TrendingUp className="h-4 w-4 sm:h-5 sm:w-5 text-green-500" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground truncate">+{pointsEarnedToday}</p>
                <p className="text-xs sm:text-sm text-muted-foreground">Earned Today</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="p-2 sm:p-2.5 rounded-lg bg-orange-500/10 flex-shrink-0">
                <TrendingDown className="h-4 w-4 sm:h-5 sm:w-5 text-orange-500" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground truncate">{pointsRedeemed}</p>
                <p className="text-xs sm:text-sm text-muted-foreground">Total Redeemed</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '150ms' }}>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="p-2 sm:p-2.5 rounded-lg bg-primary/10 flex-shrink-0">
                <Leaf className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground truncate">{(user?.totalPlastic || 0) + (user?.totalMetal || 0)}</p>
                <p className="text-xs sm:text-sm text-muted-foreground">Items Recycled</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="shadow-card animate-slide-up" style={{ animationDelay: '200ms' }}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Coins className="h-5 w-5 text-primary" />
              Points Activity
            </CardTitle>
            <CardDescription>
              Your recent points transactions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-secondary/30 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      activity.type === 'earned' 
                        ? 'bg-green-500/10' 
                        : 'bg-orange-500/10'
                    }`}>
                      {activity.type === 'earned' ? (
                        <ArrowUpRight className="h-4 w-4 text-green-500" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4 text-orange-500" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{activity.description}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </div>
                  <span className={`font-semibold ${
                    activity.type === 'earned' 
                      ? 'text-green-600' 
                      : 'text-orange-600'
                  }`}>
                    {activity.type === 'earned' ? '+' : '-'}{activity.amount}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default Wallet;
