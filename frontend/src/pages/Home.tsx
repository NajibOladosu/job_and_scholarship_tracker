import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Zap, Shield, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';

export const Home = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-block mb-6"
            >
              <div className="glass px-4 py-2 rounded-full text-sm text-accent flex items-center space-x-2">
                <Sparkles size={16} />
                <span>AI-Powered Application Tracking</span>
              </div>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 text-balance">
              Track Your Career Journey with{' '}
              <span className="gradient-text glow-text">Trackly</span>
            </h1>

            <p className="text-xl text-text-secondary mb-10 text-balance max-w-2xl mx-auto">
              Streamline your job and scholarship applications with AI-powered automation.
              Never miss a deadline. Always stay organized.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button variant="primary" size="lg" className="group">
                <Link to="/signup" className="flex items-center space-x-2">
                  <span>Start Free Trial</span>
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
              <Button variant="secondary" size="lg">
                <Link to="/demo">Watch Demo</Link>
              </Button>
            </div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto"
            >
              <Stat value="10K+" label="Active Users" />
              <Stat value="50K+" label="Applications Tracked" />
              <Stat value="99%" label="Success Rate" />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Everything You Need to <span className="gradient-text">Succeed</span>
            </h2>
            <p className="text-xl text-text-secondary max-w-2xl mx-auto">
              Powerful features designed to make your application process seamless
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<Zap className="text-accent" size={32} />}
              title="AI-Powered Extraction"
              description="Automatically extract questions from application URLs using advanced AI"
              delay={0.1}
            />
            <FeatureCard
              icon={<Sparkles className="text-accent" size={32} />}
              title="Smart Responses"
              description="Generate personalized responses based on your documents and profile"
              delay={0.2}
            />
            <FeatureCard
              icon={<Shield className="text-accent" size={32} />}
              title="Secure & Private"
              description="Your data is encrypted and secure. We never share your information"
              delay={0.3}
            />
            <FeatureCard
              icon={<TrendingUp className="text-accent" size={32} />}
              title="Track Progress"
              description="Monitor your applications with beautiful dashboards and analytics"
              delay={0.4}
            />
            <FeatureCard
              icon={<Zap className="text-accent" size={32} />}
              title="Smart Reminders"
              description="Never miss a deadline with intelligent notification system"
              delay={0.5}
            />
            <FeatureCard
              icon={<Sparkles className="text-accent" size={32} />}
              title="Document Management"
              description="Upload and manage all your application documents in one place"
              delay={0.6}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container-custom">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="card-glass p-12 text-center relative overflow-hidden"
          >
            {/* Glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-accent/0 via-accent/10 to-accent/0 animate-glow-pulse" />

            <div className="relative z-10">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">
                Ready to <span className="gradient-text">Transform</span> Your Career?
              </h2>
              <p className="text-xl text-text-secondary mb-8 max-w-2xl mx-auto">
                Join thousands of successful applicants using Trackly to land their dream opportunities
              </p>
              <Button variant="primary" size="lg" className="group">
                <Link to="/signup" className="flex items-center space-x-2">
                  <span>Get Started for Free</span>
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

const Stat = ({ value, label }: { value: string; label: string }) => (
  <div>
    <div className="text-3xl md:text-4xl font-bold gradient-text mb-1">{value}</div>
    <div className="text-sm text-text-secondary">{label}</div>
  </div>
);

const FeatureCard = ({
  icon,
  title,
  description,
  delay,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  delay: number;
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay }}
  >
    <Card variant="hover" className="h-full">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-text-primary mb-2">{title}</h3>
      <p className="text-text-secondary">{description}</p>
    </Card>
  </motion.div>
);
