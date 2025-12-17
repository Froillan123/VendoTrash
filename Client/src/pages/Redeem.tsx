import { useState } from 'react';
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
import { mockRewards, mockRedemptions, Redemption } from '@/lib/mockData';

const Redeem = () => {
  const { user, updateUserPoints } = useAuth();
  const { toast } = useToast();
  const [redemptions, setRedemptions] = useState<Redemption[]>(mockRedemptions);
  const [isRedeeming, setIsRedeeming] = useState<string | null>(null);

  const getRewardIcon = (category: string) => {
    switch (category) {
      case 'wifi': return Wifi;
      case 'data': return Smartphone;
      case 'voucher': return ShoppingBag;
      default: return Gift;
    }
  };

  const handleRedeem = async (rewardId: string, rewardName: string, pointsRequired: number) => {
    if ((user?.totalPoints || 0) < pointsRequired) {
      toast({
        title: 'Insufficient Points',
        description: `You need ${pointsRequired - (user?.totalPoints || 0)} more points`,
        variant: 'destructive',
      });
      return;
    }

    setIsRedeeming(rewardId);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Deduct points
    updateUserPoints(-pointsRequired);

    // Add redemption record
    const newRedemption: Redemption = {
      id: `r${Date.now()}`,
      userId: user?.id || '1',
      rewardName,
      pointsUsed: pointsRequired,
      timestamp: new Date().toISOString(),
      status: 'Completed',
    };
    setRedemptions(prev => [newRedemption, ...prev]);

    setIsRedeeming(null);
    
    toast({
      title: 'Redemption Successful!',
      description: `You have redeemed ${rewardName}`,
    });
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
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <Gift className="h-8 w-8 text-primary" />
            Redeem Points
          </h1>
          <p className="text-muted-foreground">
            Exchange your points for exciting rewards
          </p>
        </div>

        {/* Current Balance */}
        <Card className="mb-8 animate-slide-up">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-primary/10">
                  <Coins className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Available Points</p>
                  <p className="text-3xl font-bold text-foreground">{user?.totalPoints || 0}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Rewards Grid */}
        <div className="mb-10">
          <h2 className="text-xl font-semibold text-foreground mb-4">Available Rewards</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {mockRewards.map((reward, index) => {
              const Icon = getRewardIcon(reward.category);
              const canAfford = (user?.totalPoints || 0) >= reward.pointsRequired;
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
                    <div className="flex items-start justify-between">
                      <div className={`p-3 rounded-xl ${
                        reward.category === 'wifi' 
                          ? 'bg-blue-500/10' 
                          : reward.category === 'data' 
                            ? 'bg-purple-500/10' 
                            : 'bg-orange-500/10'
                      }`}>
                        <Icon className={`h-6 w-6 ${
                          reward.category === 'wifi' 
                            ? 'text-blue-500' 
                            : reward.category === 'data' 
                              ? 'text-purple-500' 
                              : 'text-orange-500'
                        }`} />
                      </div>
                      <Badge variant="secondary" className="font-semibold">
                        {reward.pointsRequired} pts
                      </Badge>
                    </div>
                    <CardTitle className="text-lg mt-3">{reward.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {reward.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button
                      onClick={() => handleRedeem(reward.id, reward.name, reward.pointsRequired)}
                      disabled={!canAfford || isCurrentlyRedeeming}
                      variant={canAfford ? 'eco' : 'secondary'}
                      className="w-full"
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
            })}
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
              <div className="space-y-3">
                {redemptions.map((redemption, index) => (
                  <div 
                    key={redemption.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <CheckCircle className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{redemption.rewardName}</p>
                        <p className="text-xs text-muted-foreground">{formatDate(redemption.timestamp)}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-orange-600">-{redemption.pointsUsed}</p>
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
