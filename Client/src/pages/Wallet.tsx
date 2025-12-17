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

const Wallet = () => {
  const { user } = useAuth();

  // Simulated wallet data
  const pointsEarnedToday = 8;
  const pointsRedeemed = 100;
  const remainingBalance = (user?.totalPoints || 0);

  const recentActivity = [
    { type: 'earned', amount: 2, description: 'Plastic deposit', time: '2 hours ago' },
    { type: 'earned', amount: 1, description: 'Metal deposit', time: '3 hours ago' },
    { type: 'redeemed', amount: 20, description: 'Wi-Fi voucher', time: 'Yesterday' },
    { type: 'earned', amount: 2, description: 'Plastic deposit', time: 'Yesterday' },
    { type: 'earned', amount: 2, description: 'Plastic deposit', time: '2 days ago' },
  ];

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <WalletIcon className="h-8 w-8 text-primary" />
            My Wallet
          </h1>
          <p className="text-muted-foreground">
            Track your points and balance
          </p>
        </div>

        {/* Balance Card */}
        <Card className="mb-8 overflow-hidden animate-slide-up">
          <div className="eco-gradient p-8 text-center">
            <p className="text-primary-foreground/80 text-sm mb-2">Current Balance</p>
            <div className="flex items-center justify-center gap-3">
              <Coins className="h-10 w-10 text-primary-foreground" />
              <span className="text-5xl font-bold text-primary-foreground">
                {remainingBalance}
              </span>
              <span className="text-xl text-primary-foreground/80">points</span>
            </div>
            <p className="text-primary-foreground/60 text-sm mt-4">
              Keep recycling to earn more rewards!
            </p>
          </div>
        </Card>

        {/* Stats Grid */}
        <div className="grid sm:grid-cols-3 gap-4 mb-8">
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '50ms' }}>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-green-500/10">
                <TrendingUp className="h-5 w-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">+{pointsEarnedToday}</p>
                <p className="text-xs text-muted-foreground">Earned Today</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '100ms' }}>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-orange-500/10">
                <TrendingDown className="h-5 w-5 text-orange-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{pointsRedeemed}</p>
                <p className="text-xs text-muted-foreground">Total Redeemed</p>
              </div>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '150ms' }}>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-primary/10">
                <Leaf className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{(user?.totalPlastic || 0) + (user?.totalMetal || 0)}</p>
                <p className="text-xs text-muted-foreground">Items Recycled</p>
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
