import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LayoutDashboard, Search, Recycle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { mockTransactions, mockUsers } from '@/lib/mockData';
import { useState } from 'react';

const AdminTransactions = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const getUserName = (userId: string) => {
    const user = mockUsers.find(u => u.id === userId);
    return user?.name || 'Unknown User';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const filteredTransactions = mockTransactions.filter(tx => 
    getUserName(tx.userId).toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.trashType.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <LayoutDashboard className="h-8 w-8 text-primary" />
            Transaction Monitoring
          </h1>
          <p className="text-muted-foreground">
            View all recycling transactions
          </p>
        </div>

        {/* Search */}
        <Card className="mb-6 animate-slide-up">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Transactions Table */}
        <Card className="shadow-card animate-slide-up" style={{ animationDelay: '100ms' }}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Recycle className="h-5 w-5 text-primary" />
              All Transactions ({filteredTransactions.length})
            </CardTitle>
            <CardDescription>
              Complete transaction history
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">ID</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">User</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Trash Type</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Points</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Timestamp</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTransactions.map((tx) => (
                    <tr 
                      key={tx.id} 
                      className="border-b border-border/50 hover:bg-secondary/30 transition-colors"
                    >
                      <td className="py-4 px-4 text-sm text-muted-foreground">#{tx.id}</td>
                      <td className="py-4 px-4 font-medium text-foreground">{getUserName(tx.userId)}</td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <div className={`p-1.5 rounded ${
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
                          <span className="text-sm text-foreground">{tx.trashType}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-right">
                        <span className="font-semibold text-primary">+{tx.pointsEarned}</span>
                      </td>
                      <td className="py-4 px-4 text-sm text-muted-foreground">{formatDate(tx.timestamp)}</td>
                      <td className="py-4 px-4 text-center">
                        <Badge variant={tx.status === 'Completed' ? 'default' : 'secondary'}>
                          {tx.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default AdminTransactions;
