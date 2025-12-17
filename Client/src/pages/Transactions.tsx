import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Receipt, 
  Coins, 
  Calendar,
  Package,
  CheckCircle,
  XCircle,
  ArrowUpRight
} from 'lucide-react';
import { transactionsAPI, Transaction } from '@/lib/api';

const Transactions = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 20;

  useEffect(() => {
    if (user) {
      loadTransactions();
    }
  }, [user]);

  const loadTransactions = async () => {
    try {
      setIsLoading(true);
      const response = await transactionsAPI.getByUser(skip, limit);
      // Handle paginated responses
      const txList = response.items || response;
      if (skip === 0) {
        setTransactions(txList);
      } else {
        setTransactions(prev => [...prev, ...txList]);
      }
      setHasMore(txList.length === limit);
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMore = async () => {
    if (!isLoading && hasMore) {
      const newSkip = skip + limit;
      try {
        setIsLoading(true);
        const response = await transactionsAPI.getByUser(newSkip, limit);
        const txList = response.items || response;
        setTransactions(prev => [...prev, ...txList]);
        setHasMore(txList.length === limit);
        setSkip(newSkip);
      } catch (error) {
        console.error('Error loading more transactions:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Format time helper function
  const formatTime = (dateString: string) => {
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
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Group transactions by date
  const groupedTransactions = transactions.reduce((groups, tx) => {
    const date = new Date(tx.created_at);
    const dateKey = date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
    
    if (!groups[dateKey]) {
      groups[dateKey] = [];
    }
    groups[dateKey].push(tx);
    return groups;
  }, {} as Record<string, Transaction[]>);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-6 sm:mb-8 lg:mb-10 animate-fade-in">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-2 flex items-center gap-2 sm:gap-3">
            <Receipt className="h-6 w-6 sm:h-8 sm:w-8 text-primary" />
            My Transactions
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            View your recycling transaction history
          </p>
        </div>

        {/* Transactions List */}
        {isLoading && transactions.length === 0 ? (
          <Card className="shadow-card">
            <CardContent className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-muted-foreground">Loading transactions...</p>
            </CardContent>
          </Card>
        ) : transactions.length === 0 ? (
          <Card className="shadow-card">
            <CardContent className="p-8 text-center">
              <Receipt className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">No transactions yet</p>
              <p className="text-sm text-muted-foreground mt-2">
                Start recycling to see your transaction history here
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedTransactions).map(([dateKey, txs]) => (
              <div key={dateKey} className="animate-slide-up">
                <Card className="shadow-card">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <CardTitle className="text-lg">{dateKey}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {txs.map((tx) => (
                        <div
                          key={tx.id}
                          className="flex items-center justify-between p-4 rounded-lg border-2 hover:bg-secondary/30 transition-colors"
                        >
                          <div className="flex items-center gap-4 flex-1 min-w-0">
                            <div className={`p-2.5 rounded-lg flex-shrink-0 ${
                              tx.material_type === 'PLASTIC' 
                                ? 'bg-blue-500/10' 
                                : tx.material_type === 'NON_PLASTIC'
                                  ? 'bg-amber-500/10'
                                  : 'bg-red-500/10'
                            }`}>
                              {tx.material_type === 'REJECTED' ? (
                                <XCircle className={`h-5 w-5 ${
                                  tx.material_type === 'REJECTED' ? 'text-red-500' : ''
                                }`} />
                              ) : (
                                <CheckCircle className={`h-5 w-5 ${
                                  tx.material_type === 'PLASTIC' ? 'text-blue-500' : 'text-amber-500'
                                }`} />
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge 
                                  variant={
                                    tx.material_type === 'PLASTIC' ? 'default' :
                                    tx.material_type === 'NON_PLASTIC' ? 'secondary' :
                                    'destructive'
                                  }
                                  className="text-xs"
                                >
                                  {tx.material_type === 'PLASTIC' ? 'PLASTIC' :
                                   tx.material_type === 'NON_PLASTIC' ? 'NON-PLASTIC' :
                                   'REJECTED'}
                                </Badge>
                                {tx.points_earned > 0 && (
                                  <span className="text-xs text-muted-foreground">
                                    ID: #{tx.id}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {formatTime(tx.created_at)}
                              </p>
                              {tx.confidence && (
                                <p className="text-xs text-muted-foreground mt-1">
                                  Confidence: {(tx.confidence * 100).toFixed(1)}%
                                </p>
                              )}
                            </div>
                          </div>
                          {tx.points_earned > 0 && (
                            <div className="flex items-center gap-2 flex-shrink-0">
                              <div className="text-right">
                                <div className="flex items-center gap-1 text-green-600 font-semibold">
                                  <ArrowUpRight className="h-4 w-4" />
                                  <span>+{tx.points_earned}</span>
                                </div>
                                <p className="text-xs text-muted-foreground">points</p>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}

            {/* Load More Button */}
            {hasMore && (
              <div className="text-center">
                <button
                  onClick={loadMore}
                  disabled={isLoading}
                  className="px-6 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Loading...' : 'Load More'}
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default Transactions;

