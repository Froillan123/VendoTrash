import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LayoutDashboard, Search, Recycle, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { transactionsAPI, usersAPI, Transaction, User } from '@/lib/api';
import { useState, useEffect } from 'react';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';

const ITEMS_PER_PAGE = 20;

const AdminTransactions = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    loadData(currentPage);
    // Load all users once for name lookup
    usersAPI.getAll(0, 1000).then(response => setUsers(response.items)).catch(console.error);
  }, [currentPage]);

  const loadData = async (page: number) => {
    try {
      setLoading(true);
      setError(null);
      const skip = (page - 1) * ITEMS_PER_PAGE;
      const txResponse = await transactionsAPI.getAll(skip, ITEMS_PER_PAGE);
      setTransactions(txResponse.items);
      setTotal(txResponse.total);
      setHasMore(txResponse.has_more);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load transactions');
      console.error('Error loading transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  const getPageNumbers = () => {
    const pages: (number | 'ellipsis')[] = [];
    const maxVisible = 5;
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) {
          pages.push(i);
        }
        pages.push('ellipsis');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('ellipsis');
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        pages.push('ellipsis');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i);
        }
        pages.push('ellipsis');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  const getUserName = (userId: number) => {
    const user = users.find(u => u.id === userId);
    return user?.username || `User #${userId}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const filteredTransactions = transactions.filter(tx => 
    getUserName(tx.user_id).toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.material_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-6 sm:mb-8 lg:mb-10 animate-fade-in">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-2 flex items-center gap-2 sm:gap-3">
            <LayoutDashboard className="h-6 w-6 sm:h-8 sm:w-8 text-primary" />
            Transaction Monitoring
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            View all recycling transactions
          </p>
        </div>

        {/* Search */}
        <Card className="mb-4 sm:mb-6 animate-slide-up">
          <CardContent className="p-3 sm:p-4">
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
              All Transactions ({total})
            </CardTitle>
            <CardDescription>
              Complete transaction history
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : error ? (
              <div className="text-center py-12 text-red-500">
                <p>{error}</p>
              </div>
            ) : (
              <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-3 sm:px-4 text-xs sm:text-sm font-medium text-muted-foreground">ID</th>
                        <th className="text-left py-3 px-3 sm:px-4 text-xs sm:text-sm font-medium text-muted-foreground">User</th>
                        <th className="text-left py-3 px-3 sm:px-4 text-xs sm:text-sm font-medium text-muted-foreground">Material</th>
                        <th className="text-right py-3 px-3 sm:px-4 text-xs sm:text-sm font-medium text-muted-foreground">Points</th>
                        <th className="text-left py-3 px-3 sm:px-4 text-xs sm:text-sm font-medium text-muted-foreground hidden lg:table-cell">Timestamp</th>
                        <th className="text-center py-3 px-3 sm:px-4 text-xs sm:text-sm font-medium text-muted-foreground">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTransactions.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="py-8 text-center text-sm sm:text-base text-muted-foreground">
                            No transactions found
                          </td>
                        </tr>
                      ) : (
                        filteredTransactions.map((tx) => (
                          <tr 
                            key={tx.id} 
                            className="border-b border-border/50 hover:bg-secondary/30 transition-colors"
                          >
                            <td className="py-3 sm:py-4 px-3 sm:px-4 text-xs sm:text-sm text-muted-foreground">#{tx.id}</td>
                            <td className="py-3 sm:py-4 px-3 sm:px-4">
                              <p className="text-sm sm:text-base font-medium text-foreground truncate max-w-[100px] sm:max-w-none">{getUserName(tx.user_id)}</p>
                              <p className="text-xs text-muted-foreground lg:hidden">{formatDate(tx.created_at)}</p>
                            </td>
                            <td className="py-3 sm:py-4 px-3 sm:px-4">
                              <div className="flex items-center gap-1.5 sm:gap-2">
                                <div className={`p-1 sm:p-1.5 rounded flex-shrink-0 ${
                                  tx.material_type === 'PLASTIC' 
                                    ? 'bg-blue-500/10' 
                                    : 'bg-amber-500/10'
                                }`}>
                                  <Recycle className={`h-3 w-3 sm:h-4 sm:w-4 ${
                                    tx.material_type === 'PLASTIC' 
                                      ? 'text-blue-500' 
                                      : 'text-amber-500'
                                  }`} />
                                </div>
                                <span className="text-xs sm:text-sm text-foreground truncate">{tx.material_type}</span>
                              </div>
                            </td>
                            <td className="py-3 sm:py-4 px-3 sm:px-4 text-right">
                              <span className="text-sm sm:text-base font-semibold text-primary">+{tx.points_earned}</span>
                            </td>
                            <td className="py-3 sm:py-4 px-3 sm:px-4 text-xs sm:text-sm text-muted-foreground hidden lg:table-cell">{formatDate(tx.created_at)}</td>
                            <td className="py-3 sm:py-4 px-3 sm:px-4 text-center">
                              <Badge variant={tx.status === 'Completed' ? 'default' : 'secondary'} className="text-xs">
                                {tx.status}
                              </Badge>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
          
          {/* Pagination */}
          {!loading && !error && totalPages > 1 && (
            <div className="mt-6 flex justify-center">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious 
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        if (currentPage > 1) setCurrentPage(currentPage - 1);
                      }}
                      className={currentPage === 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                    />
                  </PaginationItem>
                  
                  {getPageNumbers().map((page, index) => (
                    <PaginationItem key={index}>
                      {page === 'ellipsis' ? (
                        <PaginationEllipsis />
                      ) : (
                        <PaginationLink
                          href="#"
                          isActive={currentPage === page}
                          onClick={(e) => {
                            e.preventDefault();
                            setCurrentPage(page as number);
                          }}
                          className="cursor-pointer"
                        >
                          {page}
                        </PaginationLink>
                      )}
                    </PaginationItem>
                  ))}
                  
                  <PaginationItem>
                    <PaginationNext 
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        if (currentPage < totalPages) setCurrentPage(currentPage + 1);
                      }}
                      className={currentPage >= totalPages ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default AdminTransactions;
