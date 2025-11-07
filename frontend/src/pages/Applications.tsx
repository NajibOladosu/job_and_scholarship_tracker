import { motion } from 'framer-motion';
import { Search, Plus, MoreVertical, Clock, CheckCircle, Loader2, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { applicationsService } from '@/services/applications';
import type { Application } from '@/services/applications';

export const Applications = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        const data = await applicationsService.getAll();
        setApplications(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load applications');
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  const filteredApplications = applications.filter((app) => {
    const matchesSearch =
      app.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.company_or_institution.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || app.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

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

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">Applications</h1>
          <p className="text-text-secondary">Manage all your job and scholarship applications</p>
        </div>
        <Button variant="primary">
          <Link to="/applications/new" className="flex items-center space-x-2">
            <Plus size={20} />
            <span>New Application</span>
          </Link>
        </Button>
      </div>

      {/* Filters and Search */}
      <Card variant="glass">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary" size={20} />
              <Input
                type="text"
                placeholder="Search applications..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <FilterButton
              active={filterStatus === 'all'}
              onClick={() => setFilterStatus('all')}
            >
              All
            </FilterButton>
            <FilterButton
              active={filterStatus === 'draft'}
              onClick={() => setFilterStatus('draft')}
            >
              Draft
            </FilterButton>
            <FilterButton
              active={filterStatus === 'in_progress'}
              onClick={() => setFilterStatus('in_progress')}
            >
              In Progress
            </FilterButton>
            <FilterButton
              active={filterStatus === 'submitted'}
              onClick={() => setFilterStatus('submitted')}
            >
              Submitted
            </FilterButton>
          </div>
        </div>
      </Card>

      {/* Applications Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredApplications.map((app, index) => (
          <ApplicationCard key={app.id} application={app} delay={index * 0.1} />
        ))}
      </div>

      {filteredApplications.length === 0 && (
        <div className="text-center py-12">
          <p className="text-text-secondary text-lg">No applications found</p>
        </div>
      )}
    </div>
  );
};

const FilterButton = ({
  children,
  active,
  onClick,
}: {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
}) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
      active
        ? 'bg-accent text-black'
        : 'bg-surface border border-border text-text-secondary hover:border-accent hover:text-accent'
    }`}
  >
    {children}
  </button>
);

const ApplicationCard = ({
  application,
  delay,
}: {
  application: Application;
  delay: number;
}) => {
  const statusConfig: Record<string, { icon: React.ReactNode; color: string; bg: string; border: string; label: string }> = {
    draft: {
      icon: <Clock size={16} />,
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
      label: 'Draft',
    },
    in_progress: {
      icon: <Clock size={16} />,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      label: 'In Progress',
    },
    in_review: {
      icon: <Clock size={16} />,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      label: 'In Review',
    },
    submitted: {
      icon: <CheckCircle size={16} />,
      color: 'text-green-400',
      bg: 'bg-green-500/10',
      border: 'border-green-500/30',
      label: 'Submitted',
    },
    interview: {
      icon: <Clock size={16} />,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/30',
      label: 'Interview',
    },
    offer: {
      icon: <CheckCircle size={16} />,
      color: 'text-accent',
      bg: 'bg-accent/10',
      border: 'border-accent/30',
      label: 'Offer',
    },
    rejected: {
      icon: <AlertCircle size={16} />,
      color: 'text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      label: 'Rejected',
    },
    withdrawn: {
      icon: <AlertCircle size={16} />,
      color: 'text-gray-400',
      bg: 'bg-gray-500/10',
      border: 'border-gray-500/30',
      label: 'Withdrawn',
    },
  };

  const status = statusConfig[application.status] || statusConfig.draft;
  const questionCount = application.question_count || 0;
  const responseCount = application.response_count || 0;
  const progress = questionCount > 0 ? (responseCount / questionCount) * 100 : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
    >
      <Link to={`/applications/${application.id}`}>
        <Card variant="hover">
          <div className="space-y-4">
            {/* Header */}
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-lg font-bold text-text-primary mb-1">
                  {application.title}
                </h3>
                <p className="text-text-secondary">{application.company_or_institution}</p>
              </div>
              <button className="text-text-secondary hover:text-accent transition-colors">
                <MoreVertical size={20} />
              </button>
            </div>

            {/* Status Badge */}
            <div className="flex items-center justify-between">
              <span
                className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium border ${status.bg} ${status.color} ${status.border}`}
              >
                {status.icon}
                <span>{status.label}</span>
              </span>
              <span
                className={`text-xs font-medium px-2 py-1 rounded ${
                  application.priority === 'high'
                    ? 'bg-red-500/10 text-red-400'
                    : application.priority === 'medium'
                    ? 'bg-yellow-500/10 text-yellow-400'
                    : 'bg-gray-500/10 text-gray-400'
                }`}
              >
                {application.priority.toUpperCase()}
              </span>
            </div>

            {/* Progress */}
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-text-secondary">Progress</span>
                <span className="text-accent font-medium">
                  {responseCount}/{questionCount}
                </span>
              </div>
              <div className="w-full bg-surface rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ delay: delay + 0.2, duration: 0.6 }}
                  className="h-full bg-accent rounded-full"
                />
              </div>
            </div>

            {/* Deadline */}
            <div className="flex items-center space-x-2 text-sm text-text-secondary">
              <Clock size={16} />
              <span>Deadline: {new Date(application.deadline).toLocaleDateString()}</span>
            </div>
          </div>
        </Card>
      </Link>
    </motion.div>
  );
};
