import { motion } from 'framer-motion';
import { FileText, Clock, CheckCircle, AlertCircle, TrendingUp, Plus, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { applicationsService } from '@/services/applications';
import type { Application, ApplicationStats } from '@/services/applications';

export const Dashboard = () => {
  const [stats, setStats] = useState<ApplicationStats | null>(null);
  const [recentApplications, setRecentApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsData, applicationsData] = await Promise.all([
          applicationsService.getStats(),
          applicationsService.getAll(),
        ]);
        setStats(statsData);
        // Get the 4 most recent applications
        setRecentApplications(applicationsData.slice(0, 4));
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 text-accent animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card variant="glass" className="p-8">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-500 text-center">{error}</p>
        </Card>
      </div>
    );
  }

  // Calculate stats values
  const totalApplications = stats?.total || 0;
  const inProgress = (stats?.by_status?.draft || 0) + (stats?.by_status?.in_review || 0);
  const completed = stats?.by_status?.submitted || 0;
  const pending = stats?.by_status?.interview || 0;

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
          value={totalApplications.toString()}
          delay={0.1}
        />
        <StatCard
          icon={<Clock className="text-blue-400" size={24} />}
          label="In Progress"
          value={inProgress.toString()}
          delay={0.2}
        />
        <StatCard
          icon={<CheckCircle className="text-green-400" size={24} />}
          label="Completed"
          value={completed.toString()}
          delay={0.3}
        />
        <StatCard
          icon={<AlertCircle className="text-yellow-400" size={24} />}
          label="Pending"
          value={pending.toString()}
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
              {recentApplications.length > 0 ? (
                recentApplications.map((app) => (
                  <ApplicationItem
                    key={app.id}
                    id={app.id}
                    title={`${app.position_title} at ${app.company_name}`}
                    status={app.status}
                    deadline={app.deadline}
                  />
                ))
              ) : (
                <p className="text-text-secondary text-center py-8">
                  No applications yet. Create your first application to get started!
                </p>
              )}
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
  delay,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
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
          <p className="text-3xl font-bold text-text-primary">{value}</p>
        </div>
        <div className="p-3 rounded-lg glass">
          {icon}
        </div>
      </div>
    </Card>
  </motion.div>
);

const ApplicationItem = ({
  id,
  title,
  status,
  deadline,
}: {
  id: number;
  title: string;
  status: string;
  deadline: string;
}) => {
  // Map status to colors
  const getStatusColor = (status: string) => {
    const statusMap: Record<string, string> = {
      draft: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
      submitted: 'bg-green-500/10 text-green-400 border-green-500/30',
      in_review: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
      interview: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      offer: 'bg-accent/10 text-accent border-accent/30',
      rejected: 'bg-red-500/10 text-red-400 border-red-500/30',
      withdrawn: 'bg-gray-500/10 text-gray-400 border-gray-500/30',
    };
    return statusMap[status] || statusMap.draft;
  };

  // Format status for display
  const formatStatus = (status: string) => {
    return status
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Calculate deadline display
  const getDeadlineDisplay = (deadline: string) => {
    if (!deadline) return 'No deadline';
    const deadlineDate = new Date(deadline);
    const today = new Date();
    const diffTime = deadlineDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return 'Overdue';
    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return '1 day left';
    if (diffDays <= 7) return `${diffDays} days left`;
    if (diffDays <= 30) return `${Math.ceil(diffDays / 7)} weeks left`;
    return deadlineDate.toLocaleDateString();
  };

  return (
    <Link to={`/applications/${id}`}>
      <div className="flex items-center justify-between p-4 rounded-lg bg-surface/50 hover:bg-surface transition-colors cursor-pointer">
        <div className="flex-1">
          <h3 className="text-text-primary font-medium mb-1">{title}</h3>
          <p className="text-text-secondary text-sm">{getDeadlineDisplay(deadline)}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(status)}`}>
          {formatStatus(status)}
        </span>
      </div>
    </Link>
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
