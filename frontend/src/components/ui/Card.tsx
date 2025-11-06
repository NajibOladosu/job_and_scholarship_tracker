import { motion } from 'framer-motion';
import { cn } from '@/lib/utils.ts';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'glass' | 'hover';
  className?: string;
  onClick?: () => void;
}

export const Card = ({ children, variant = 'default', className, onClick }: CardProps) => {
  const variants = {
    default: 'rounded-xl bg-surface border border-border p-5',
    glass: 'rounded-xl glass p-5',
    hover: 'rounded-xl bg-surface border border-border p-5 hover:border-accent hover:shadow-glow cursor-pointer',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={variant === 'hover' ? { scale: 1.02, boxShadow: '0 0 12px rgba(0, 255, 136, 0.25)' } : undefined}
      className={cn(variants[variant], 'transition-all duration-200', className)}
      onClick={onClick}
    >
      {children}
    </motion.div>
  );
};
