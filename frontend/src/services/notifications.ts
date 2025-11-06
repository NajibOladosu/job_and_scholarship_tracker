/**
 * Notifications API Service
 */
import api from '@/lib/api';

export interface Notification {
  id: number;
  notification_type: 'deadline' | 'status_change' | 'reminder' | 'general';
  title: string;
  message: string;
  link?: string;
  is_read: boolean;
  created_at: string;
}

export const notificationsService = {
  /**
   * Get all notifications
   */
  async getAll(): Promise<Notification[]> {
    const response = await api.get<Notification[]>('/notifications/');
    return response.data;
  },

  /**
   * Get unread notifications
   */
  async getUnread(): Promise<Notification[]> {
    const response = await api.get<Notification[]>('/notifications/unread/');
    return response.data;
  },

  /**
   * Mark notification as read
   */
  async markRead(id: number): Promise<Notification> {
    const response = await api.post<Notification>(`/notifications/${id}/mark_read/`);
    return response.data;
  },

  /**
   * Mark all notifications as read
   */
  async markAllRead(): Promise<{ message: string }> {
    const response = await api.post('/notifications/mark_all_read/');
    return response.data;
  },

  /**
   * Delete notification
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/notifications/${id}/`);
  },
};
