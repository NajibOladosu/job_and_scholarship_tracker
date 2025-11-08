import { motion } from 'framer-motion';
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save, Link as LinkIcon, Loader2, AlertCircle } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { applicationsService } from '@/services/applications';

export const ApplicationForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    application_type: 'job' as 'job' | 'scholarship',
    company_name: '',
    position_title: '',
    application_url: '',
    deadline: '',
    priority: 'medium' as 'high' | 'medium' | 'low',
    location: '',
    salary_range: '',
    is_remote: false,
    job_description: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const application = await applicationsService.create({
        ...formData,
        status: 'draft',
      });
      navigate(`/applications/${application.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create application');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Link to="/applications">
          <Button variant="ghost">
            <ArrowLeft size={20} />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-text-primary">New Application</h1>
          <p className="text-text-secondary">Create a new job or scholarship application</p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center gap-2"
        >
          <AlertCircle className="text-red-500" size={20} />
          <p className="text-red-500 text-sm">{error}</p>
        </motion.div>
      )}

      {/* Form */}
      <Card variant="glass">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Application Type */}
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Type <span className="text-red-400">*</span>
            </label>
            <div className="flex gap-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="application_type"
                  value="job"
                  checked={formData.application_type === 'job'}
                  onChange={(e) =>
                    setFormData({ ...formData, application_type: e.target.value as 'job' })
                  }
                  className="w-4 h-4 text-accent focus:ring-accent"
                />
                <span className="text-text-primary">Job</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="application_type"
                  value="scholarship"
                  checked={formData.application_type === 'scholarship'}
                  onChange={(e) =>
                    setFormData({ ...formData, application_type: e.target.value as 'scholarship' })
                  }
                  className="w-4 h-4 text-accent focus:ring-accent"
                />
                <span className="text-text-primary">Scholarship</span>
              </label>
            </div>
          </div>

          {/* Quick URL Entry */}
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              <LinkIcon className="inline mr-2" size={16} />
              Application URL
            </label>
            <Input
              type="url"
              value={formData.application_url}
              onChange={(e) => setFormData({ ...formData, application_url: e.target.value })}
              placeholder="https://example.com/jobs/senior-developer"
            />
            <p className="text-xs text-text-secondary mt-1">
              Paste the URL to auto-extract questions (requires AI features)
            </p>
          </div>

          {/* Basic Information */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Company/Organization <span className="text-red-400">*</span>
              </label>
              <Input
                type="text"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                placeholder="Acme Inc."
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Position/Program Title <span className="text-red-400">*</span>
              </label>
              <Input
                type="text"
                value={formData.position_title}
                onChange={(e) => setFormData({ ...formData, position_title: e.target.value })}
                placeholder="Senior Software Engineer"
                required
              />
            </div>
          </div>

          {/* Deadline and Priority */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Deadline</label>
              <Input
                type="date"
                value={formData.deadline}
                onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Priority</label>
              <select
                value={formData.priority}
                onChange={(e) =>
                  setFormData({ ...formData, priority: e.target.value as 'high' | 'medium' | 'low' })
                }
                className="w-full px-4 py-2 rounded-lg bg-surface border border-border text-text-primary focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all duration-200"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          {/* Location and Salary */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Location</label>
              <Input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="San Francisco, CA"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Salary/Award Range
              </label>
              <Input
                type="text"
                value={formData.salary_range}
                onChange={(e) => setFormData({ ...formData, salary_range: e.target.value })}
                placeholder="$100,000 - $150,000"
              />
            </div>
          </div>

          {/* Remote Work */}
          <div>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_remote}
                onChange={(e) => setFormData({ ...formData, is_remote: e.target.checked })}
                className="w-4 h-4 rounded border-border bg-surface checked:bg-accent checked:border-accent focus:ring-2 focus:ring-accent/20"
              />
              <span className="text-text-primary">Remote work option</span>
            </label>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Job/Program Description
            </label>
            <textarea
              value={formData.job_description}
              onChange={(e) => setFormData({ ...formData, job_description: e.target.value })}
              placeholder="Paste the job description or program details here..."
              rows={8}
              className="w-full px-4 py-2 rounded-lg bg-surface border border-border text-text-primary placeholder:text-text-secondary focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all duration-200 resize-none"
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3">
            <Link to="/applications">
              <Button type="button" variant="ghost">
                Cancel
              </Button>
            </Link>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={18} />
                  Creating...
                </>
              ) : (
                <>
                  <Save className="mr-2" size={18} />
                  Create Application
                </>
              )}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};
