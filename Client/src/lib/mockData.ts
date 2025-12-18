// Mock Data for VendoTrash System

export interface User {
  id: string;
  name: string;
  email: string;
  totalPoints: number;
  totalPlastic: number;
  totalMetal: number;
  totalTransactions: number;
  status: 'Active' | 'Inactive';
  createdAt: string;
}

export interface Transaction {
  id: string;
  userId: string;
  trashType: 'PLASTIC' | 'METAL';
  pointsEarned: number;
  timestamp: string;
  status: 'Completed' | 'Pending';
}

export interface Redemption {
  id: string;
  userId: string;
  rewardName: string;
  pointsUsed: number;
  timestamp: string;
  status: 'Completed' | 'Pending';
}

export interface Reward {
  id: string;
  name: string;
  description: string;
  pointsRequired: number;
  icon: string;
  category: 'wifi' | 'data' | 'voucher';
}

export interface Machine {
  id: string;
  name: string;
  status: 'Online' | 'Offline' | 'Maintenance';
  lastActivity: string;
  totalCollected: number;
  binCapacity: number;
  location: string;
}

// Mock Users
export const mockUsers: User[] = [
  { id: '1', name: 'Juan Dela Cruz', email: 'juan@email.com', totalPoints: 245, totalPlastic: 89, totalMetal: 34, totalTransactions: 123, status: 'Active', createdAt: '2024-01-15' },
  { id: '2', name: 'Maria Santos', email: 'maria@email.com', totalPoints: 180, totalPlastic: 65, totalMetal: 25, totalTransactions: 90, status: 'Active', createdAt: '2024-02-20' },
  { id: '3', name: 'Pedro Garcia', email: 'pedro@email.com', totalPoints: 320, totalPlastic: 120, totalMetal: 40, totalTransactions: 160, status: 'Active', createdAt: '2024-01-08' },
  { id: '4', name: 'Ana Reyes', email: 'ana@email.com', totalPoints: 95, totalPlastic: 35, totalMetal: 12, totalTransactions: 47, status: 'Active', createdAt: '2024-03-01' },
  { id: '5', name: 'Carlos Lopez', email: 'carlos@email.com', totalPoints: 410, totalPlastic: 150, totalMetal: 55, totalTransactions: 205, status: 'Active', createdAt: '2023-12-10' },
];

// Mock Transactions
export const mockTransactions: Transaction[] = [
  { id: 't1', userId: '1', trashType: 'PLASTIC', pointsEarned: 2, timestamp: '2024-12-17T09:30:00', status: 'Completed' },
  { id: 't2', userId: '1', trashType: 'METAL', pointsEarned: 1, timestamp: '2024-12-17T08:15:00', status: 'Completed' },
  { id: 't3', userId: '1', trashType: 'PLASTIC', pointsEarned: 2, timestamp: '2024-12-16T14:45:00', status: 'Completed' },
  { id: 't4', userId: '1', trashType: 'PLASTIC', pointsEarned: 2, timestamp: '2024-12-16T10:20:00', status: 'Completed' },
  { id: 't5', userId: '1', trashType: 'METAL', pointsEarned: 1, timestamp: '2024-12-15T16:00:00', status: 'Completed' },
  { id: 't6', userId: '2', trashType: 'PLASTIC', pointsEarned: 2, timestamp: '2024-12-17T11:00:00', status: 'Completed' },
  { id: 't7', userId: '3', trashType: 'METAL', pointsEarned: 1, timestamp: '2024-12-17T07:45:00', status: 'Completed' },
];

// Mock Redemptions
export const mockRedemptions: Redemption[] = [
  { id: 'r1', userId: '1', rewardName: 'Free Wi-Fi (1 hour)', pointsUsed: 20, timestamp: '2024-12-16T12:00:00', status: 'Completed' },
  { id: 'r2', userId: '1', rewardName: 'Mobile Data (100MB)', pointsUsed: 30, timestamp: '2024-12-14T09:30:00', status: 'Completed' },
  { id: 'r3', userId: '1', rewardName: 'Local Store Voucher', pointsUsed: 50, timestamp: '2024-12-10T15:00:00', status: 'Completed' },
];

// Mock Rewards
export const mockRewards: Reward[] = [
  { id: 'w1', name: 'Free Wi-Fi (1 hour)', description: 'Get 1 hour of high-speed internet access', pointsRequired: 20, icon: 'wifi', category: 'wifi' },
  { id: 'w2', name: 'Mobile Data (100MB)', description: 'Receive 100MB mobile data for any network', pointsRequired: 30, icon: 'smartphone', category: 'data' },
  { id: 'w3', name: 'Local Store Voucher', description: 'P50 voucher for partner local stores', pointsRequired: 50, icon: 'shopping-bag', category: 'voucher' },
  { id: 'w4', name: 'Premium Wi-Fi (1 day)', description: 'Full day unlimited internet access', pointsRequired: 80, icon: 'wifi', category: 'wifi' },
  { id: 'w5', name: 'Mobile Data (500MB)', description: 'Receive 500MB mobile data for any network', pointsRequired: 100, icon: 'smartphone', category: 'data' },
  { id: 'w6', name: 'Premium Voucher', description: 'P200 voucher for partner stores', pointsRequired: 150, icon: 'gift', category: 'voucher' },
];

// Mock Machines
export const mockMachines: Machine[] = [
  { id: 'm1', name: 'VT-001', status: 'Online', lastActivity: '2024-12-17T09:30:00', totalCollected: 1250, binCapacity: 65, location: 'Building A - Ground Floor' },
  { id: 'm2', name: 'VT-002', status: 'Online', lastActivity: '2024-12-17T09:15:00', totalCollected: 890, binCapacity: 42, location: 'Building B - Lobby' },
  { id: 'm3', name: 'VT-003', status: 'Maintenance', lastActivity: '2024-12-16T18:00:00', totalCollected: 2100, binCapacity: 95, location: 'Cafeteria' },
  { id: 'm4', name: 'VT-004', status: 'Online', lastActivity: '2024-12-17T08:45:00', totalCollected: 560, binCapacity: 28, location: 'Library - Entrance' },
];

// Analytics Data
export const analyticsData = {
  totalUsers: 156,
  totalTransactions: 4521,
  totalPlastic: 3200,
  totalMetal: 1321,
  totalPointsIssued: 7721,
  totalPointsRedeemed: 4850,
  
  // Daily transactions for chart
  dailyTransactions: [
    { day: 'Mon', plastic: 45, metal: 20 },
    { day: 'Tue', plastic: 52, metal: 25 },
    { day: 'Wed', plastic: 48, metal: 22 },
    { day: 'Thu', plastic: 61, metal: 30 },
    { day: 'Fri', plastic: 55, metal: 28 },
    { day: 'Sat', plastic: 38, metal: 15 },
    { day: 'Sun', plastic: 32, metal: 12 },
  ],
  
  // Monthly data
  monthlyData: [
    { month: 'Jan', transactions: 320 },
    { month: 'Feb', transactions: 380 },
    { month: 'Mar', transactions: 420 },
    { month: 'Apr', transactions: 490 },
    { month: 'May', transactions: 550 },
    { month: 'Jun', transactions: 610 },
  ],
  
  // Redemption breakdown
  redemptionBreakdown: [
    { name: 'Wi-Fi', value: 45, color: 'hsl(150, 61%, 30%)' },
    { name: 'Mobile Data', value: 35, color: 'hsl(145, 63%, 42%)' },
    { name: 'Vouchers', value: 20, color: 'hsl(140, 40%, 60%)' },
  ],
};

// Current logged in user (simulated)
export const currentUser: User = mockUsers[0];
