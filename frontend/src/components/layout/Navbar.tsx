import { motion } from 'framer-motion';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../ui/Button';

export const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 glass-strong"
    >
      <div className="container-custom">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-2xl font-bold"
            >
              <span className="text-text-primary">Track</span>
              <span className="gradient-text">ly</span>
            </motion.div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <NavLink to="/features">Features</NavLink>
            <NavLink to="/pricing">Pricing</NavLink>
            <NavLink to="/about">About</NavLink>
          </div>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Button variant="ghost" size="sm">
              <Link to="/login">Log In</Link>
            </Button>
            <Button variant="primary" size="sm">
              <Link to="/signup">Start Free Trial</Link>
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-text-primary hover:text-accent transition-colors"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden py-4 border-t border-border"
          >
            <div className="flex flex-col space-y-4">
              <MobileNavLink to="/features">Features</MobileNavLink>
              <MobileNavLink to="/pricing">Pricing</MobileNavLink>
              <MobileNavLink to="/about">About</MobileNavLink>
              <div className="pt-4 border-t border-border flex flex-col space-y-2">
                <Button variant="ghost" size="sm">
                  <Link to="/login">Log In</Link>
                </Button>
                <Button variant="primary" size="sm">
                  <Link to="/signup">Start Free Trial</Link>
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  );
};

const NavLink = ({ to, children }: { to: string; children: React.ReactNode }) => (
  <Link
    to={to}
    className="text-text-secondary hover:text-accent transition-colors duration-200 font-medium"
  >
    {children}
  </Link>
);

const MobileNavLink = ({ to, children }: { to: string; children: React.ReactNode }) => (
  <Link
    to={to}
    className="text-text-primary hover:text-accent transition-colors duration-200 font-medium py-2"
  >
    {children}
  </Link>
);
