import { motion } from 'framer-motion';
import { Bell, CheckCircle, AlertCircle, Info, Trash2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

const mockNotifications = [
  {
    id: 1,
    type: 'deadline',
    title: 'Application deadline approaching',
    message: 'Your application for Software Engineer at Google is due in 2 days',
    time: '2 hours ago',
    read: false,
  },
  {
    id: 2,
    type: 'success',
    title: 'Application submitted',
    message: 'Your Product Manager application at Meta has been successfully submitted',
    time: '5 hours ago',
    read: false,
  },
  {
    id: 3,
    type: 'info',
    title: 'Document processed',
    message: 'Your resume has been processed and is ready to use',
    time: '1 day ago',
    read: true,
  },
  {
    id: 4,
    type: 'deadline',
    title: 'Response generation complete',
    message: 'AI has generated responses for your Data Scientist application',
    time: '2 days ago',
    read: true,
  },
];

export const Notifications = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-text-primary mb-2">Notifications</h1>
          <p className="text-text-secondary">Stay updated with your applications</p>
        </div>
        <Button variant="secondary" size="sm">
          Mark All as Read
        </Button>
      </div>

      {/* Notifications List */}
      <div className="space-y-4">
        {mockNotifications.map((notification, index) => (
          <NotificationCard
            key={notification.id}
            notification={notification}
            delay={index * 0.1}
          />
        ))}
      </div>

      {mockNotifications.length === 0 && (
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
}: {
  notification: typeof mockNotifications[0];
  delay: number;
}) => {
  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="text-green-400" size={24} />;
      case 'deadline':
        return <AlertCircle className="text-yellow-400" size={24} />;
      case 'info':
        return <Info className="text-blue-400" size={24} />;
      default:
        return <Bell className="text-text-secondary" size={24} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
    >
      <Card
        variant="glass"
        className={`transition-all duration-200 ${
          !notification.read ? 'border-accent/30 bg-accent/5' : ''
        }`}
      >
        <div className="flex items-start space-x-4">
          {/* Icon */}
          <div className="p-3 rounded-lg glass">{getIcon()}</div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-2">
              <h3
                className={`font-bold ${
                  !notification.read ? 'text-text-primary' : 'text-text-secondary'
                }`}
              >
                {notification.title}
              </h3>
              {!notification.read && (
                <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0 mt-2" />
              )}
            </div>
            <p className="text-text-secondary text-sm mb-2">
              {notification.message}
            </p>
            <div className="flex items-center justify-between">
              <span className="text-text-secondary text-xs">{notification.time}</span>
              <button className="text-red-400 hover:text-red-300 transition-colors p-2">
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};
