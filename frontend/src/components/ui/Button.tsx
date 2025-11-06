import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'ref'> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button = ({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) => {
  const baseStyles = 'font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-accent/50';

  const variants = {
    primary: 'bg-accent text-black hover:bg-accent-hover hover:shadow-glow',
    secondary: 'bg-surface border border-border text-text-primary hover:border-accent hover:text-accent',
    ghost: 'bg-transparent text-text-secondary hover:bg-surface hover:text-text-primary',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-lg',
    md: 'px-4 py-2 rounded-lg',
    lg: 'px-6 py-3 text-lg rounded-xl',
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </motion.button>
  );
};
