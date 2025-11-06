import { motion } from 'framer-motion';
import { User, Mail, Phone, Edit2, Save } from 'lucide-react';
import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export const Profile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    bio: 'Software Engineer with 5+ years of experience in full-stack development.',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">Profile</h1>
          <p className="text-text-secondary">Manage your account information</p>
        </div>
        {!isEditing ? (
          <Button variant="secondary" onClick={() => setIsEditing(true)}>
            <Edit2 size={20} className="mr-2" />
            Edit Profile
          </Button>
        ) : (
          <div className="flex space-x-2">
            <Button variant="secondary" onClick={() => setIsEditing(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={() => setIsEditing(false)}>
              <Save size={20} className="mr-2" />
              Save Changes
            </Button>
          </div>
        )}
      </div>

      {/* Profile Card */}
      <Card variant="glass" className="p-8">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Avatar Section */}
          <div className="flex flex-col items-center space-y-4">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="relative"
            >
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-accent to-accent-light p-1">
                <div className="w-full h-full rounded-full bg-surface flex items-center justify-center">
                  <User size={48} className="text-accent" />
                </div>
              </div>
              <div className="absolute bottom-0 right-0 w-10 h-10 rounded-full bg-accent flex items-center justify-center cursor-pointer hover:bg-accent-hover transition-colors shadow-glow">
                <Edit2 size={16} className="text-black" />
              </div>
            </motion.div>
            <p className="text-text-secondary text-sm">Click to upload photo</p>
          </div>

          {/* Form Section */}
          <div className="flex-1 space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                disabled={!isEditing}
              />
              <Input
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                disabled={!isEditing}
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <Input
                label="Phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                disabled={!isEditing}
              />
              <Input
                label="Location"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                disabled={!isEditing}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Bio
              </label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleInputChange}
                disabled={!isEditing}
                rows={4}
                className="w-full px-4 py-2 rounded-lg bg-surface border border-border text-text-primary placeholder:text-text-secondary focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all duration-200 disabled:opacity-50"
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Account Stats */}
      <div className="grid md:grid-cols-3 gap-6">
        <StatCard
          icon={<User className="text-accent" size={24} />}
          label="Applications"
          value="24"
        />
        <StatCard
          icon={<Mail className="text-blue-400" size={24} />}
          label="Documents"
          value="12"
        />
        <StatCard
          icon={<Phone className="text-green-400" size={24} />}
          label="Member Since"
          value="2024"
        />
      </div>

      {/* Danger Zone */}
      <Card variant="glass" className="border-red-500/30">
        <h3 className="text-xl font-bold text-red-400 mb-4">Danger Zone</h3>
        <p className="text-text-secondary mb-4">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <Button
          variant="secondary"
          className="!text-red-400 !border-red-500/30 hover:!bg-red-500/10"
        >
          Delete Account
        </Button>
      </Card>
    </div>
  );
};

const StatCard = ({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) => (
  <Card variant="glass" className="text-center">
    <div className="flex justify-center mb-3">{icon}</div>
    <div className="text-3xl font-bold text-text-primary mb-1">{value}</div>
    <div className="text-sm text-text-secondary">{label}</div>
  </Card>
);
