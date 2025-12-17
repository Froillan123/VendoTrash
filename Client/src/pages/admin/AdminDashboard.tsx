import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Users, 
  Recycle, 
  Coins, 
  TrendingUp,
  ArrowUpRight,
  BarChart3
} from 'lucide-react';
import { analyticsData } from '@/lib/mockData';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const AdminDashboard = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <BarChart3 className="h-8 w-8 text-primary" />
            Admin Dashboard
          </h1>
          <p className="text-muted-foreground">
            Monitor system performance and analytics
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
          <Card className="stat-card animate-slide-up">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-primary" />
                <span className="text-xs text-muted-foreground">Total Users</span>
              </div>
              <p className="text-2xl font-bold text-foreground">{analyticsData.totalUsers}</p>
              <span className="text-xs text-green-600 flex items-center gap-1">
                <ArrowUpRight className="h-3 w-3" /> +12%
              </span>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '50ms' }}>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-blue-500" />
                <span className="text-xs text-muted-foreground">Transactions</span>
              </div>
              <p className="text-2xl font-bold text-foreground">{analyticsData.totalTransactions.toLocaleString()}</p>
              <span className="text-xs text-green-600 flex items-center gap-1">
                <ArrowUpRight className="h-3 w-3" /> +8%
              </span>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '100ms' }}>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <Recycle className="h-4 w-4 text-blue-500" />
                <span className="text-xs text-muted-foreground">Plastic</span>
              </div>
              <p className="text-2xl font-bold text-foreground">{analyticsData.totalPlastic.toLocaleString()}</p>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '150ms' }}>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <Recycle className="h-4 w-4 text-amber-500" />
                <span className="text-xs text-muted-foreground">Metal</span>
              </div>
              <p className="text-2xl font-bold text-foreground">{analyticsData.totalMetal.toLocaleString()}</p>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '200ms' }}>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <Coins className="h-4 w-4 text-green-500" />
                <span className="text-xs text-muted-foreground">Points Issued</span>
              </div>
              <p className="text-2xl font-bold text-foreground">{analyticsData.totalPointsIssued.toLocaleString()}</p>
            </div>
          </Card>
          
          <Card className="stat-card animate-slide-up" style={{ animationDelay: '250ms' }}>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <Coins className="h-4 w-4 text-orange-500" />
                <span className="text-xs text-muted-foreground">Points Redeemed</span>
              </div>
              <p className="text-2xl font-bold text-foreground">{analyticsData.totalPointsRedeemed.toLocaleString()}</p>
            </div>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Plastic vs Metal Bar Chart */}
          <Card className="shadow-card animate-slide-up" style={{ animationDelay: '300ms' }}>
            <CardHeader>
              <CardTitle className="text-lg">Weekly Deposits</CardTitle>
              <CardDescription>Plastic vs Metal collection this week</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analyticsData.dailyTransactions}>
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
                  <LineChart data={analyticsData.monthlyData}>
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
            <div className="h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analyticsData.redemptionBreakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {analyticsData.redemptionBreakdown.map((entry, index) => (
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
      </main>

      <Footer />
    </div>
  );
};

export default AdminDashboard;
