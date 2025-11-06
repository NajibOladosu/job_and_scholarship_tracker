import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  FileText,
  Upload,
  Bell,
  User,
  LogOut,
  ChevronRight,
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils.ts';

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: FileText, label: 'Applications', path: '/applications' },
  { icon: Upload, label: 'Documents', path: '/documents' },
  { icon: Bell, label: 'Notifications', path: '/notifications' },
  { icon: User, label: 'Profile', path: '/profile' },
];

export const Sidebar = () => {
  const location = useLocation();

  return (
    <motion.aside
      initial={{ x: -280 }}
      animate={{ x: 0 }}
      className="fixed left-0 top-0 h-screen w-64 glass-strong border-r border-border z-40"
    >
      <div className="flex flex-col h-full p-4">
        {/* Logo */}
        <Link to="/dashboard" className="flex items-center space-x-2 mb-8 mt-2">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="text-2xl font-bold"
          >
            <span className="text-text-primary">Track</span>
            <span className="gradient-text">ly</span>
          </motion.div>
        </Link>

        {/* Navigation */}
        <nav className="flex-1 space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;

            return (
              <Link key={item.path} to={item.path}>
                <motion.div
                  whileHover={{ x: 4 }}
                  className={cn(
                    'flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-200',
                    isActive
                      ? 'bg-accent/10 text-accent border border-accent/30 shadow-glow'
                      : 'text-text-secondary hover:bg-surface hover:text-text-primary'
                  )}
                >
                  <div className="flex items-center space-x-3">
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  {isActive && <ChevronRight size={16} className="text-accent" />}
                </motion.div>
              </Link>
            );
          })}
        </nav>

        {/* Logout Button */}
        <motion.button
          whileHover={{ x: 4 }}
          className="flex items-center space-x-3 px-4 py-3 rounded-lg text-text-secondary hover:bg-red-500/10 hover:text-red-500 transition-all duration-200 w-full"
        >
          <LogOut size={20} />
          <span className="font-medium">Logout</span>
        </motion.button>
      </div>
    </motion.aside>
  );
};
