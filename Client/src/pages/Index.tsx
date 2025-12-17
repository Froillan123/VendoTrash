import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Recycle, Leaf, ArrowRight, Coins, Gift, Smartphone } from 'lucide-react';
import logo from '@/assets/logo.png';

const Index = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Decorative Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-accent/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 right-1/4 w-72 h-72 bg-primary/5 rounded-full blur-3xl" />
      </div>

      {/* Hero Section */}
      <header className="flex-1 flex flex-col">
        {/* Navigation */}
        <nav className="container mx-auto px-4 py-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src={logo} alt="VendoTrash" className="h-12 w-auto" />
            <span className="font-bold text-xl text-foreground hidden sm:block">VendoTrash</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link to="/register">
              <Button variant="eco">Get Started</Button>
            </Link>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="flex-1 container mx-auto px-4 flex flex-col items-center justify-center text-center py-16">
          <div className="animate-float mb-8">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 rounded-full blur-2xl scale-150" />
              <div className="relative bg-card p-6 rounded-full shadow-glow border border-border/50">
                <Recycle className="h-16 w-16 text-primary" />
              </div>
            </div>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 max-w-4xl animate-fade-in">
            Smart Trash Vending Machine for a{' '}
            <span className="text-gradient">Cleaner, Smarter</span> Future
          </h1>
          
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mb-10 animate-fade-in" style={{ animationDelay: '100ms' }}>
            Earn rewards by recycling. Deposit your plastic and metal waste, collect points, and redeem them for Wi-Fi, mobile data, and local store vouchers.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 animate-fade-in" style={{ animationDelay: '200ms' }}>
            <Link to="/register">
              <Button variant="eco" size="xl" className="min-w-[200px]">
                Start Recycling
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="xl" className="min-w-[200px]">
                Already a Member
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section className="bg-secondary/30 py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-foreground mb-4">How It Works</h2>
          <p className="text-center text-muted-foreground mb-12 max-w-xl mx-auto">
            Simple steps to earn rewards while helping the environment
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-card p-8 rounded-2xl shadow-card border border-border/50 text-center animate-slide-up" style={{ animationDelay: '0ms' }}>
              <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-blue-500/10 flex items-center justify-center">
                <Recycle className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">Deposit Trash</h3>
              <p className="text-muted-foreground">
                Insert your plastic or metal waste into the VendoTrash machine. Our smart sensors detect and classify your items.
              </p>
            </div>

            <div className="bg-card p-8 rounded-2xl shadow-card border border-border/50 text-center animate-slide-up" style={{ animationDelay: '100ms' }}>
              <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-primary/10 flex items-center justify-center">
                <Coins className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">Earn Points</h3>
              <p className="text-muted-foreground">
                Get 2 points for plastic and 1 point for metal. Points are automatically credited to your account.
              </p>
            </div>

            <div className="bg-card p-8 rounded-2xl shadow-card border border-border/50 text-center animate-slide-up" style={{ animationDelay: '200ms' }}>
              <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-orange-500/10 flex items-center justify-center">
                <Gift className="h-8 w-8 text-orange-500" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">Redeem Rewards</h3>
              <p className="text-muted-foreground">
                Exchange your points for Wi-Fi access, mobile data, or vouchers at partner local stores.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Rewards Preview */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-foreground mb-4">Available Rewards</h2>
          <p className="text-center text-muted-foreground mb-12 max-w-xl mx-auto">
            Turn your eco-friendly actions into valuable rewards
          </p>

          <div className="flex flex-wrap justify-center gap-6">
            <div className="flex items-center gap-3 bg-card px-6 py-4 rounded-xl shadow-soft border border-border/50">
              <div className="p-2 rounded-lg bg-blue-500/10">
                <Smartphone className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <p className="font-medium text-foreground">Free Wi-Fi</p>
                <p className="text-sm text-muted-foreground">From 20 points</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3 bg-card px-6 py-4 rounded-xl shadow-soft border border-border/50">
              <div className="p-2 rounded-lg bg-purple-500/10">
                <Smartphone className="h-5 w-5 text-purple-500" />
              </div>
              <div>
                <p className="font-medium text-foreground">Mobile Data</p>
                <p className="text-sm text-muted-foreground">From 30 points</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3 bg-card px-6 py-4 rounded-xl shadow-soft border border-border/50">
              <div className="p-2 rounded-lg bg-orange-500/10">
                <Gift className="h-5 w-5 text-orange-500" />
              </div>
              <div>
                <p className="font-medium text-foreground">Store Vouchers</p>
                <p className="text-sm text-muted-foreground">From 50 points</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <img src={logo} alt="VendoTrash" className="h-8 w-auto" />
              <span className="text-sm text-muted-foreground">
                VendoTrash — Reward-Based Recycling System | IoT & Web-Based Solution
              </span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Leaf className="h-4 w-4 text-primary" />
              <span className="text-xs">Making a cleaner, smarter future</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
