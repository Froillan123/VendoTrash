import { useState, useEffect, useRef } from 'react';
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
  Zap,
  Play,
  CheckCircle
} from 'lucide-react';
import { transactionsAPI, vendoAPI, Transaction } from '@/lib/api';
import { API_BASE_URL } from '@/lib/apiConfig';


interface DetectionHistoryItem {
  material_type: string;
  confidence: number;
  points_earned: number;
  timestamp: string;
  transaction_id?: string;
  status?: string;
}

const Dashboard = () => {
  const { user, updateUserStats, refreshUser, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [detectionHistory, setDetectionHistory] = useState<DetectionHistoryItem[]>([]);
  const [isPreparing, setIsPreparing] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [isEndingSession, setIsEndingSession] = useState(false);
  
  // WebSocket connection management
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  // Load transactions and detection history on mount - wait for user to be authenticated
  useEffect(() => {
    if (user && isAuthenticated) {
      loadTransactions();
      loadDetectionHistory();
    }
  }, [user, isAuthenticated]);

  // WebSocket connection for real-time detection updates
  useEffect(() => {
    if (!isReady || !user) {
      // Close WebSocket if session is not active
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      return;
    }

    const connectWebSocket = () => {
      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close();
      }

      // Get WebSocket URL (replace http with ws)
      const wsUrl = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://');
      const wsEndpoint = `${wsUrl}/api/vendo/ws/detection-updates/${user.id}`;
      
      console.log('🔌 Connecting to WebSocket:', wsEndpoint);
      const ws = new WebSocket(wsEndpoint);
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected for real-time updates');
        reconnectAttemptsRef.current = 0; // Reset reconnect attempts
        
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'detection_update') {
            // Update detection history immediately (real-time!)
            const newDetection = message.data;
            setDetectionHistory(prev => {
              const newHistory = [newDetection, ...prev];
              return newHistory.slice(0, 5); // Keep max 5
            });
            
            // Refresh transactions and user stats
            loadTransactions();
            refreshUser();
            
            // Show toast notification
            const isRejected = newDetection.material_type === 'REJECTED';
            toast({
              title: isRejected ? '❌ Item Rejected' : '✅ Item Detected',
              description: `${newDetection.material_type} - ${newDetection.points_earned} points`,
            });
          } else if (message.type === 'connection') {
            console.log('📡 WebSocket connection confirmed:', message.message);
          } else if (message.type === 'pong' || message.type === 'keepalive') {
            // Keepalive messages, no action needed
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };
      
      ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected', event.code, event.reason);
        
        // Only reconnect if session is still active and we haven't exceeded max attempts
        if (isReady && user && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000); // Exponential backoff, max 10s
          
          console.log(`🔄 Reconnecting WebSocket in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          console.error('❌ Max WebSocket reconnection attempts reached');
          toast({
            title: '⚠️ Connection Lost',
            description: 'Real-time updates unavailable. Please refresh the page.',
            variant: 'destructive',
          });
        }
      };
      
      wsRef.current = ws;
    };

    // Connect WebSocket
    connectWebSocket();

    // Cleanup on unmount or when dependencies change
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      reconnectAttemptsRef.current = 0;
    };
  }, [isReady, user]);

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

  const loadDetectionHistory = async () => {
    if (!user) return;
    
    try {
      const response = await vendoAPI.getDetectionHistory();
      if (response.status === 'success' && response.history) {
        setDetectionHistory(response.history);
      }
    } catch (error) {
      console.error('Error loading detection history:', error);
    }
  };

  const handlePrepareInsert = async () => {
    if (!user || isPreparing) return;

    setIsPreparing(true);
    
    try {
      const result = await vendoAPI.prepareInsert();
      
      if (result.status === 'success') {
        setIsReady(true);
        toast({
          title: "✅ System Ready",
          description: "Session created. Insert trash into the machine now. Detection will trigger automatically.",
        });
        
        // Immediately refresh to get latest state
        loadDetectionHistory();
        loadTransactions();
        refreshUser();
        
        // Reset ready state after 10 minutes (session TTL)
        setTimeout(() => {
          setIsReady(false);
        }, 600000);
      } else {
        throw new Error(result.message || 'Failed to prepare insert session');
      }
    } catch (error: any) {
      console.error('Error preparing insert:', error);
      toast({
        title: '❌ Error',
        description: error.message || 'Failed to prepare insert session. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsPreparing(false);
    }
  };

  const handleEndSession = async () => {
    if (!user || isEndingSession) return;

    setIsEndingSession(true);
    
    try {
      const result = await vendoAPI.endSession();
      
      if (result.status === 'success' || result.status === 'not_found') {
        setIsReady(false);
        // Refresh data after ending session
        loadDetectionHistory();
        loadTransactions();
        refreshUser();
        toast({
          title: "✅ Session Ended",
          description: result.message || "Session ended successfully. Click 'Insert Trash' to start a new session.",
        });
      } else {
        throw new Error(result.message || 'Failed to end session');
      }
    } catch (error: any) {
      console.error('Error ending session:', error);
      toast({
        title: '❌ Error',
        description: error.message || 'Failed to end session. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsEndingSession(false);
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
              {/* Detection History Display (Max 5) */}
              {detectionHistory.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs sm:text-sm font-semibold text-muted-foreground">Latest Detections (Max 5)</p>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {detectionHistory.map((detection, index) => {
                      const isRejected = detection.material_type === 'REJECTED' || detection.status === 'rejected';
                      return (
                        <div 
                          key={index}
                          className={`p-3 rounded-lg border-2 ${
                            isRejected
                              ? 'bg-red-50 border-red-200 dark:bg-red-950/20 dark:border-red-800'
                              : detection.material_type === 'PLASTIC' 
                                ? 'bg-blue-50 border-blue-200 dark:bg-blue-950/20 dark:border-blue-800' 
                                : 'bg-amber-50 border-amber-200 dark:bg-amber-950/20 dark:border-amber-800'
                          } animate-scale-in`}
                          style={{ animationDelay: `${index * 50}ms` }}
                        >
                          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                            <div className="flex-1">
                              <p className={`text-sm sm:text-base font-bold ${
                                isRejected 
                                  ? 'text-red-600' 
                                  : detection.material_type === 'PLASTIC' 
                                    ? 'text-blue-600' 
                                    : 'text-amber-600'
                              }`}>
                                {isRejected 
                                  ? '❌ REJECTED' 
                                  : detection.material_type === 'PLASTIC' 
                                    ? '✅ PLASTIC' 
                                    : '✅ CAN/METAL'}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {detection.confidence > 0 
                                  ? `Confidence: ${detection.confidence.toFixed(1)}%`
                                  : 'No confidence data'}
                              </p>
                            </div>
                            <div className="text-left sm:text-right">
                              <p className={`text-sm sm:text-base font-bold ${
                                isRejected ? 'text-red-600' : 'text-primary'
                              }`}>
                                {isRejected ? '0 pts' : `+${detection.points_earned} pts`}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {new Date(detection.timestamp).toLocaleTimeString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Fallback: Show latest transaction if no detection history */}
              {detectionHistory.length === 0 && transactions.length > 0 && (
                <div className={`p-3 sm:p-4 rounded-lg border-2 ${
                  transactions[0].material_type === 'PLASTIC' 
                    ? 'bg-blue-50 border-blue-200 dark:bg-blue-950/20 dark:border-blue-800' 
                    : 'bg-amber-50 border-amber-200 dark:bg-amber-950/20 dark:border-amber-800'
                } animate-scale-in`}>
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
                    <div>
                      <p className="text-xs sm:text-sm text-muted-foreground">Latest Detection</p>
                      <p className={`text-base sm:text-lg font-bold ${
                        transactions[0].material_type === 'PLASTIC' ? 'text-blue-600' : 'text-amber-600'
                      }`}>
                        {transactions[0].material_type === 'PLASTIC' ? '✅ PLASTIC' : '✅ CAN/METAL'}
                      </p>
                    </div>
                    <div className="text-left sm:text-right">
                      <p className="text-xs sm:text-sm text-muted-foreground">Points Earned</p>
                      <p className="text-base sm:text-lg font-bold text-primary">
                        +{transactions[0].points_earned}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Insert Button */}
              <div className="space-y-2">
                <Button
                  onClick={handlePrepareInsert}
                  disabled={isPreparing || isReady || !user}
                  variant="eco"
                  size="lg"
                  className="w-full h-12 sm:h-14 text-base sm:text-lg"
                >
                  {isPreparing ? (
                    <>
                      <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Preparing...
                    </>
                  ) : isReady ? (
                    <>
                      <CheckCircle className="h-5 w-5 mr-2" />
                      Ready - Insert Trash Now
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5 mr-2" />
                      Insert Trash
                    </>
                  )}
                </Button>

                {/* End Session Button */}
                {isReady && (
                  <Button
                    onClick={handleEndSession}
                    disabled={isEndingSession || !user}
                    variant="outline"
                    size="lg"
                    className="w-full h-12 sm:h-14 text-base sm:text-lg"
                  >
                    {isEndingSession ? (
                      <>
                        <div className="h-5 w-5 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
                        Ending Session...
                      </>
                    ) : (
                      <>
                        End Session
                      </>
                    )}
                  </Button>
                )}
              </div>

              {isReady && (
                <div className="p-4 rounded-lg bg-green-50 border-2 border-green-200 dark:bg-green-950/20 dark:border-green-800">
                  <p className="text-sm font-semibold text-green-800 dark:text-green-200 mb-1">
                    ✅ System Ready
                  </p>
                  <p className="text-xs text-green-700 dark:text-green-300">
                    Insert trash into the machine now. The system will automatically detect and classify your item.
                  </p>
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
