import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Cpu, MapPin, Clock, Package } from 'lucide-react';
import { mockMachines } from '@/lib/mockData';

const AdminMachines = () => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Online': return 'bg-green-500';
      case 'Offline': return 'bg-red-500';
      case 'Maintenance': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      
      <main className="flex-1 content-container">
        {/* Page Header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
            <Cpu className="h-8 w-8 text-primary" />
            Machine Status
          </h1>
          <p className="text-muted-foreground">
            Monitor VendoTrash machines
          </p>
        </div>

        {/* Machines Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {mockMachines.map((machine, index) => (
            <Card 
              key={machine.id} 
              className="shadow-card animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="h-5 w-5 text-primary" />
                    {machine.name}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <div className={`w-2.5 h-2.5 rounded-full ${getStatusColor(machine.status)}`} />
                    <Badge variant={machine.status === 'Online' ? 'default' : 'secondary'}>
                      {machine.status}
                    </Badge>
                  </div>
                </div>
                <CardDescription className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  {machine.location}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    Last Activity
                  </span>
                  <span className="text-foreground">{formatDate(machine.lastActivity)}</span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2 text-muted-foreground">
                    <Package className="h-4 w-4" />
                    Items Collected
                  </span>
                  <span className="font-semibold text-foreground">{machine.totalCollected.toLocaleString()}</span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Bin Capacity</span>
                    <span className={`font-medium ${
                      machine.binCapacity > 80 ? 'text-red-500' : 
                      machine.binCapacity > 60 ? 'text-yellow-500' : 'text-green-500'
                    }`}>
                      {machine.binCapacity}%
                    </span>
                  </div>
                  <Progress 
                    value={machine.binCapacity} 
                    className={`h-2 ${
                      machine.binCapacity > 80 ? '[&>div]:bg-red-500' : 
                      machine.binCapacity > 60 ? '[&>div]:bg-yellow-500' : '[&>div]:bg-green-500'
                    }`}
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AdminMachines;
