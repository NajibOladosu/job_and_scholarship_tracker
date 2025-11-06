import { motion } from 'framer-motion';
import { FileText, Clock, CheckCircle, AlertCircle, TrendingUp, Plus } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export const Dashboard = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">Dashboard</h1>
          <p className="text-text-secondary">Welcome back! Here's your application overview.</p>
        </div>
        <Button variant="primary">
          <Link to="/applications/new" className="flex items-center space-x-2">
            <Plus size={20} />
            <span>New Application</span>
          </Link>
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<FileText className="text-accent" size={24} />}
          label="Total Applications"
          value="24"
          change="+12%"
          positive={true}
          delay={0.1}
        />
        <StatCard
          icon={<Clock className="text-blue-400" size={24} />}
          label="In Progress"
          value="8"
          change="+3"
          positive={true}
          delay={0.2}
        />
        <StatCard
          icon={<CheckCircle className="text-green-400" size={24} />}
          label="Completed"
          value="12"
          change="+5"
          positive={true}
          delay={0.3}
        />
        <StatCard
          icon={<AlertCircle className="text-yellow-400" size={24} />}
          label="Pending"
          value="4"
          change="-2"
          positive={false}
          delay={0.4}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Applications */}
        <div className="lg:col-span-2">
          <Card variant="glass">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-text-primary">Recent Applications</h2>
              <Link to="/applications" className="text-accent hover:text-accent-hover text-sm font-medium">
                View All
              </Link>
            </div>
            <div className="space-y-4">
              <ApplicationItem
                title="Software Engineer at Google"
                status="In Progress"
                deadline="2 days left"
                statusColor="blue"
              />
              <ApplicationItem
                title="Product Manager at Meta"
                status="Submitted"
                deadline="5 days left"
                statusColor="green"
              />
              <ApplicationItem
                title="Data Scientist at Amazon"
                status="Draft"
                deadline="1 week left"
                statusColor="yellow"
              />
              <ApplicationItem
                title="Full Stack Developer at Microsoft"
                status="In Progress"
                deadline="3 days left"
                statusColor="blue"
              />
            </div>
          </Card>
        </div>

        {/* Quick Stats */}
        <div className="space-y-6">
          {/* Activity Card */}
          <Card variant="glass">
            <div className="flex items-center space-x-3 mb-4">
              <TrendingUp className="text-accent" size={24} />
              <h2 className="text-xl font-bold text-text-primary">Activity</h2>
            </div>
            <div className="space-y-4">
              <ActivityItem
                action="Application submitted"
                target="Software Engineer at Google"
                time="2 hours ago"
              />
              <ActivityItem
                action="Document uploaded"
                target="Resume_2024.pdf"
                time="5 hours ago"
              />
              <ActivityItem
                action="Response generated"
                target="Product Manager application"
                time="1 day ago"
              />
            </div>
          </Card>

          {/* Quick Actions */}
          <Card variant="glass">
            <h2 className="text-xl font-bold text-text-primary mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <QuickActionButton to="/applications/new">
                <Plus size={18} />
                <span>New Application</span>
              </QuickActionButton>
              <QuickActionButton to="/documents/upload">
                <FileText size={18} />
                <span>Upload Document</span>
              </QuickActionButton>
              <QuickActionButton to="/applications">
                <CheckCircle size={18} />
                <span>View All Applications</span>
              </QuickActionButton>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({
  icon,
  label,
  value,
  change,
  positive,
  delay,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  change: string;
  positive: boolean;
  delay: number;
}) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
  >
    <Card variant="glass" className="hover:border-accent transition-all duration-200">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-text-secondary text-sm mb-2">{label}</p>
          <p className="text-3xl font-bold text-text-primary mb-1">{value}</p>
          <p className={`text-sm font-medium ${positive ? 'text-green-400' : 'text-red-400'}`}>
            {change} this month
          </p>
        </div>
        <div className="p-3 rounded-lg glass">
          {icon}
        </div>
      </div>
    </Card>
  </motion.div>
);

const ApplicationItem = ({
  title,
  status,
  deadline,
  statusColor,
}: {
  title: string;
  status: string;
  deadline: string;
  statusColor: 'blue' | 'green' | 'yellow';
}) => {
  const colors = {
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    green: 'bg-green-500/10 text-green-400 border-green-500/30',
    yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  };

  return (
    <div className="flex items-center justify-between p-4 rounded-lg bg-surface/50 hover:bg-surface transition-colors cursor-pointer">
      <div className="flex-1">
        <h3 className="text-text-primary font-medium mb-1">{title}</h3>
        <p className="text-text-secondary text-sm">{deadline}</p>
      </div>
      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${colors[statusColor]}`}>
        {status}
      </span>
    </div>
  );
};

const ActivityItem = ({
  action,
  target,
  time,
}: {
  action: string;
  target: string;
  time: string;
}) => (
  <div className="flex items-start space-x-3 p-3 rounded-lg bg-surface/30">
    <div className="w-2 h-2 rounded-full bg-accent mt-2" />
    <div className="flex-1">
      <p className="text-text-primary text-sm font-medium">{action}</p>
      <p className="text-text-secondary text-xs">{target}</p>
      <p className="text-text-secondary text-xs mt-1">{time}</p>
    </div>
  </div>
);

const QuickActionButton = ({ to, children }: { to: string; children: React.ReactNode }) => (
  <Link to={to}>
    <motion.button
      whileHover={{ x: 4 }}
      className="w-full flex items-center space-x-2 p-3 rounded-lg bg-surface/50 hover:bg-surface hover:border-accent border border-transparent transition-all text-text-primary"
    >
      {children}
    </motion.button>
  </Link>
);
