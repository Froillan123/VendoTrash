import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { 
  Gift, 
  Wifi, 
  Smartphone, 
  ShoppingBag,
  Coins,
  CheckCircle,
  Clock
} from 'lucide-react';
import { rewardsAPI, redemptionsAPI, Reward, Redemption } from '@/lib/api';

const Redeem = () => {
  const { user, refreshUser } = useAuth();
  const { toast } = useToast();
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [redemptions, setRedemptions] = useState<Redemption[]>([]);
  const [isRedeeming, setIsRedeeming] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [rewardsData, redemptionsResponse] = await Promise.all([
        rewardsAPI.getAll(true), // Only active rewards
        redemptionsAPI.getByUser(0, 100)
      ]);
      setRewards(rewardsData);
      // Handle paginated response - extract items if it's a paginated response
      const redemptionsArray = Array.isArray(redemptionsResponse) 
        ? redemptionsResponse 
        : redemptionsResponse.items;
      setRedemptions(redemptionsArray);
    } catch (error) {
      console.error('Error loading redeem data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRewardIcon = (category: string) => {
    switch (category) {
      case 'wifi': return Wifi;
      case 'data': return Smartphone;
      case 'voucher': return ShoppingBag;
      default: return Gift;
    }
  };

  const handleRedeem = async (rewardId: number, rewardName: string, pointsRequired: number) => {
    if ((user?.totalPoints || 0) < pointsRequired) {
      toast({
        title: 'Insufficient Points',
        description: `You need ${pointsRequired - (user?.totalPoints || 0)} more points`,
        variant: 'destructive',
      });
      return;
    }

    setIsRedeeming(rewardId);
    
    try {
      // Create redemption via API
      const newRedemption = await redemptionsAPI.create({
        reward_id: rewardId,
        points_used: pointsRequired,
      });
      
      // Reload data
      await loadData();
      await refreshUser();
      
      toast({
        title: 'Redemption Successful!',
        description: `You have redeemed ${rewardName}`,
      });
    } catch (error: any) {
      toast({
        title: 'Redemption Failed',
        description: error.message || 'Failed to redeem reward',
        variant: 'destructive',
      });
    } finally {
      setIsRedeeming(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-6 sm:mb-8 lg:mb-10 animate-fade-in">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-2 flex items-center gap-2 sm:gap-3">
            <Gift className="h-6 w-6 sm:h-8 sm:w-8 text-primary" />
            Redeem Points
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Exchange your points for exciting rewards
          </p>
        </div>

        {/* Current Balance */}
        <Card className="mb-6 sm:mb-8 animate-slide-up">
          <CardContent className="p-4 sm:p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="p-2 sm:p-3 rounded-xl bg-primary/10 flex-shrink-0">
                  <Coins className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
                </div>
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground">Available Points</p>
                  <p className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground">{user?.totalPoints || 0}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Rewards Grid */}
        <div className="mb-8 sm:mb-10">
          <h2 className="text-lg sm:text-xl lg:text-2xl font-semibold text-foreground mb-3 sm:mb-4">Available Rewards</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-5">
            {isLoading ? (
              <p className="col-span-full text-center text-muted-foreground py-8">Loading rewards...</p>
            ) : rewards.length === 0 ? (
              <p className="col-span-full text-center text-muted-foreground py-8">No rewards available</p>
            ) : (
              rewards.map((reward, index) => {
                const Icon = getRewardIcon(reward.category);
                const canAfford = (user?.totalPoints || 0) >= reward.points_required;
                const isCurrentlyRedeeming = isRedeeming === reward.id;

              return (
                <Card 
                  key={reward.id} 
                  className={`shadow-card hover:shadow-glow transition-all duration-300 animate-slide-up ${
                    !canAfford ? 'opacity-60' : ''
                  }`}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className={`p-2 sm:p-3 rounded-xl flex-shrink-0 ${
                        reward.category === 'wifi' 
                          ? 'bg-blue-500/10' 
                          : reward.category === 'data' 
                            ? 'bg-purple-500/10' 
                            : 'bg-orange-500/10'
                      }`}>
                        <Icon className={`h-5 w-5 sm:h-6 sm:w-6 ${
                          reward.category === 'wifi' 
                            ? 'text-blue-500' 
                            : reward.category === 'data' 
                              ? 'text-purple-500' 
                              : 'text-orange-500'
                        }`} />
                      </div>
                      <Badge variant="secondary" className="font-semibold text-xs sm:text-sm flex-shrink-0">
                        {reward.points_required} pts
                      </Badge>
                    </div>
                    <CardTitle className="text-base sm:text-lg mt-2 sm:mt-3">{reward.name}</CardTitle>
                    <CardDescription className="text-xs sm:text-sm line-clamp-2">
                      {reward.description || 'No description available'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button
                      onClick={() => handleRedeem(reward.id, reward.name, reward.points_required)}
                      disabled={!canAfford || isCurrentlyRedeeming || !reward.is_active}
                      variant={canAfford ? 'eco' : 'secondary'}
                      className="w-full h-10 sm:h-11 text-sm sm:text-base"
                    >
                      {isCurrentlyRedeeming ? (
                        <span className="flex items-center gap-2">
                          <span className="h-4 w-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                          Redeeming...
                        </span>
                      ) : canAfford ? (
                        <>
                          <Gift className="h-4 w-4" />
                          Redeem Now
                        </>
                      ) : (
                        'Not Enough Points'
                      )}
                    </Button>
                  </CardContent>
                </Card>
              );
            }))}
          </div>
        </div>

        {/* Redemption History */}
        <Card className="shadow-card animate-slide-up" style={{ animationDelay: '300ms' }}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Redemption History
            </CardTitle>
            <CardDescription>
              Your past reward redemptions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {redemptions.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">
                No redemptions yet. Start redeeming your points!
              </p>
            ) : (
              <div className="space-y-2 sm:space-y-3">
                {redemptions.map((redemption, index) => (
                  <div 
                    key={redemption.id}
                    className="flex items-center justify-between p-3 sm:p-4 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors"
                  >
                    <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
                      <div className="p-1.5 sm:p-2 rounded-lg bg-primary/10 flex-shrink-0">
                        <CheckCircle className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-primary" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm sm:text-base font-medium text-foreground truncate">{redemption.reward?.name || 'Reward'}</p>
                        <p className="text-xs text-muted-foreground">{formatDate(redemption.created_at)}</p>
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0 ml-2">
                      <p className="text-sm sm:text-base font-semibold text-orange-600">-{redemption.points_used}</p>
                      <Badge variant="secondary" className="text-xs">{redemption.status}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>

      <Footer />
    </div>
  );
};

export default Redeem;
