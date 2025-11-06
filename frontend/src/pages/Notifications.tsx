import { motion } from 'framer-motion';
import { Bell, CheckCircle, AlertCircle, Info, Trash2, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { notificationsService } from '@/services/notifications';
import type { Notification } from '@/services/notifications';

export const Notifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const data = await notificationsService.getAll();
      setNotifications(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationsService.markAllRead();
      await fetchNotifications();
    } catch (err: any) {
      console.error('Failed to mark all as read:', err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await notificationsService.delete(id);
      await fetchNotifications();
    } catch (err: any) {
      console.error('Failed to delete notification:', err);
    }
  };

  const handleMarkRead = async (id: number) => {
    try {
      await notificationsService.markRead(id);
      await fetchNotifications();
    } catch (err: any) {
      console.error('Failed to mark as read:', err);
    }
  };

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">Notifications</h1>
          <p className="text-text-secondary">Stay updated with your applications</p>
        </div>
        <Button variant="secondary" size="sm" onClick={handleMarkAllRead}>
          Mark All as Read
        </Button>
      </div>

      {/* Notifications List */}
      {notifications.length > 0 ? (
        <div className="space-y-4">
          {notifications.map((notification, index) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              delay={index * 0.1}
              onDelete={handleDelete}
              onMarkRead={handleMarkRead}
            />
          ))}
        </div>
      ) : (
        <Card variant="glass" className="p-12 text-center">
          <Bell className="mx-auto text-text-secondary mb-4" size={48} />
          <h3 className="text-xl font-bold text-text-primary mb-2">
            No notifications
          </h3>
          <p className="text-text-secondary">
            You're all caught up! Check back later for updates.
          </p>
        </Card>
      )}
    </div>
  );
};

const NotificationCard = ({
  notification,
  delay,
  onDelete,
  onMarkRead,
}: {
  notification: Notification;
  delay: number;
  onDelete: (id: number) => void;
  onMarkRead: (id: number) => void;
}) => {
  const getIcon = () => {
    switch (notification.notification_type) {
      case 'status_change':
        return <CheckCircle className="text-green-400" size={24} />;
      case 'deadline':
        return <AlertCircle className="text-yellow-400" size={24} />;
      case 'reminder':
        return <Info className="text-blue-400" size={24} />;
      case 'general':
        return <Bell className="text-text-secondary" size={24} />;
      default:
        return <Bell className="text-text-secondary" size={24} />;
    }
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
    >
      <Card
        variant="glass"
        className={`transition-all duration-200 cursor-pointer ${
          !notification.is_read ? 'border-accent/30 bg-accent/5' : ''
        }`}
        onClick={() => !notification.is_read && onMarkRead(notification.id)}
      >
        <div className="flex items-start space-x-4">
          {/* Icon */}
          <div className="p-3 rounded-lg glass">{getIcon()}</div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-2">
              <h3
                className={`font-bold ${
                  !notification.is_read ? 'text-text-primary' : 'text-text-secondary'
                }`}
              >
                {notification.title}
              </h3>
              {!notification.is_read && (
                <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0 mt-2" />
              )}
            </div>
            <p className="text-text-secondary text-sm mb-2">
              {notification.message}
            </p>
            <div className="flex items-center justify-between">
              <span className="text-text-secondary text-xs">{getTimeAgo(notification.created_at)}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(notification.id);
                }}
                className="text-red-400 hover:text-red-300 transition-colors p-2"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};
