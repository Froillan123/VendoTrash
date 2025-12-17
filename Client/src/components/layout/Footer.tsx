import { Leaf, Recycle } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-card border-t border-border py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Recycle className="h-5 w-5 text-primary" />
            <span className="text-sm">
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
  );
};

export default Footer;
