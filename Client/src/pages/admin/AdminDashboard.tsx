import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Users, 
  Recycle, 
  Coins, 
  TrendingUp,
  ArrowUpRight,
  BarChart3,
  Loader2
} from 'lucide-react';
import { usersAPI, transactionsAPI, redemptionsAPI, User, Transaction, Redemption } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { useState, useEffect } from 'react';

const AdminDashboard = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [redemptions, setRedemptions] = useState<Redemption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [usersData, txData, redData] = await Promise.all([
        usersAPI.getAll(0, 1000),
        transactionsAPI.getAll(0, 1000),
        redemptionsAPI.getAll(0, 1000) // Admin endpoint to get all redemptions
      ]);
      setUsers(usersData.items);
      setTransactions(txData.items);
      setRedemptions(redData.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Calculate stats from real data
  const totalUsers = users.length;
  const totalTransactions = transactions.length;
  const totalPlastic = transactions.filter(tx => tx.material_type === 'PLASTIC').length;
  const totalMetal = transactions.filter(tx => tx.material_type === 'NON_PLASTIC').length;
  const totalPointsIssued = transactions.reduce((sum, tx) => sum + tx.points_earned, 0);
  const totalPointsRedeemed = redemptions.reduce((sum, r) => sum + r.points_used, 0);

  // Generate chart data from real transactions
  const getDailyTransactions = () => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toISOString().split('T')[0];
    });

    return last7Days.map(day => {
      const dayTransactions = transactions.filter(tx => 
        tx.created_at.startsWith(day)
      );
      return {
        day: new Date(day).toLocaleDateString('en-US', { weekday: 'short' }),
        plastic: dayTransactions.filter(tx => tx.material_type === 'PLASTIC').length,
        metal: dayTransactions.filter(tx => tx.material_type === 'NON_PLASTIC').length,
      };
    });
  };

  const getMonthlyData = () => {
    const last6Months = Array.from({ length: 6 }, (_, i) => {
      const date = new Date();
      date.setMonth(date.getMonth() - (5 - i));
      return date.toISOString().slice(0, 7); // YYYY-MM
    });

    return last6Months.map(month => {
      const monthTransactions = transactions.filter(tx => 
        tx.created_at.startsWith(month)
      );
      return {
        month: new Date(month + '-01').toLocaleDateString('en-US', { month: 'short' }),
        transactions: monthTransactions.length,
      };
    });
  };

  const getRedemptionBreakdown = () => {
    const categories = ['wifi', 'data', 'voucher'];
    const colors = ['#3b82f6', '#10b981', '#f59e0b'];
    
    return categories.map((cat, index) => {
      const count = redemptions.filter(r => r.reward?.category === cat).length;
      return {
        name: cat.charAt(0).toUpperCase() + cat.slice(1),
        value: count,
        color: colors[index],
      };
    });
  };
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-6 sm:mb-8 lg:mb-10 animate-fade-in">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-2 flex items-center gap-2 sm:gap-3">
            <BarChart3 className="h-6 w-6 sm:h-8 sm:w-8 text-primary" />
            Admin Dashboard
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Monitor system performance and analytics
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-500">
            <p>{error}</p>
          </div>
        ) : (
          <>
            {/* Stats Overview */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 xl:grid-cols-6 gap-3 sm:gap-4 lg:gap-5 mb-6 sm:mb-8">
              <Card className="stat-card animate-slide-up">
                <div className="flex flex-col gap-1 sm:gap-2">
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <Users className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-primary flex-shrink-0" />
                    <span className="text-xs sm:text-sm text-muted-foreground truncate">Total Users</span>
                  </div>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">{totalUsers.toLocaleString()}</p>
                </div>
              </Card>
              
              <Card className="stat-card animate-slide-up" style={{ animationDelay: '50ms' }}>
                <div className="flex flex-col gap-1 sm:gap-2">
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <TrendingUp className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm text-muted-foreground truncate">Transactions</span>
                  </div>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">{totalTransactions.toLocaleString()}</p>
                </div>
              </Card>
              
              <Card className="stat-card animate-slide-up" style={{ animationDelay: '100ms' }}>
                <div className="flex flex-col gap-1 sm:gap-2">
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <Recycle className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-blue-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm text-muted-foreground truncate">Plastic</span>
                  </div>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">{totalPlastic.toLocaleString()}</p>
                </div>
              </Card>
              
              <Card className="stat-card animate-slide-up" style={{ animationDelay: '150ms' }}>
                <div className="flex flex-col gap-1 sm:gap-2">
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <Recycle className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-amber-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm text-muted-foreground truncate">Non-Plastic</span>
                  </div>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">{totalMetal.toLocaleString()}</p>
                </div>
              </Card>
              
              <Card className="stat-card animate-slide-up" style={{ animationDelay: '200ms' }}>
                <div className="flex flex-col gap-1 sm:gap-2">
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <Coins className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-green-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm text-muted-foreground truncate">Points Issued</span>
                  </div>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">{totalPointsIssued.toLocaleString()}</p>
                </div>
              </Card>
              
              <Card className="stat-card animate-slide-up" style={{ animationDelay: '250ms' }}>
                <div className="flex flex-col gap-1 sm:gap-2">
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <Coins className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-orange-500 flex-shrink-0" />
                    <span className="text-xs sm:text-sm text-muted-foreground truncate">Points Redeemed</span>
                  </div>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground">{totalPointsRedeemed.toLocaleString()}</p>
                </div>
              </Card>
            </div>

        {/* Charts Row */}
        <div className="grid lg:grid-cols-2 gap-4 sm:gap-5 lg:gap-6 mb-6 sm:mb-8">
          {/* Plastic vs Metal Bar Chart */}
          <Card className="shadow-card animate-slide-up" style={{ animationDelay: '300ms' }}>
            <CardHeader>
              <CardTitle className="text-lg">Weekly Deposits</CardTitle>
              <CardDescription>Plastic vs Metal collection this week</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={getDailyTransactions()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="day" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                    <YAxis tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'hsl(var(--card))', 
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px'
                      }} 
                    />
                    <Bar dataKey="plastic" fill="hsl(210, 80%, 55%)" radius={[4, 4, 0, 0]} name="Plastic" />
                    <Bar dataKey="metal" fill="hsl(40, 90%, 55%)" radius={[4, 4, 0, 0]} name="Metal" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Monthly Transactions Line Chart */}
          <Card className="shadow-card animate-slide-up" style={{ animationDelay: '350ms' }}>
            <CardHeader>
              <CardTitle className="text-lg">Monthly Transactions</CardTitle>
              <CardDescription>Transaction trend over 6 months</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={getMonthlyData()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="month" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                    <YAxis tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'hsl(var(--card))', 
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px'
                      }} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="transactions" 
                      stroke="hsl(var(--primary))" 
                      strokeWidth={3}
                      dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Redemption Pie Chart */}
        <Card className="shadow-card animate-slide-up" style={{ animationDelay: '400ms' }}>
          <CardHeader>
            <CardTitle className="text-lg">Redemption Breakdown</CardTitle>
            <CardDescription>Distribution of reward redemptions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-56 sm:h-64 lg:h-72 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={getRedemptionBreakdown()}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {getRedemptionBreakdown().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--card))', 
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            </CardContent>
          </Card>
          </>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default AdminDashboard;
