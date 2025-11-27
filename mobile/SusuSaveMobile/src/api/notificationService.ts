import { apiClient } from './client';
import { Notification, NotificationListResponse } from '../types/api';

// Wait for API client to be ready
const waitForApiClient = async () => {
  let attempts = 0;
  while (!apiClient && attempts < 10) {
    await new Promise(resolve => setTimeout(resolve, 100));
    attempts++;
  }
  if (!apiClient) {
    throw new Error('API client not available');
  }
  return apiClient;
};

export const notificationService = {
  /**
   * Get notifications for the current user
   */
  async getNotifications(
    unreadOnly: boolean = false,
    limit: number = 50,
    offset: number = 0
  ): Promise<NotificationListResponse> {
    const client = await waitForApiClient();
    const response = await client.get('/notifications', {
      params: {
        unread_only: unreadOnly,
        limit,
        offset,
      },
    });
    return response.data;
  },

  /**
   * Get only unread notifications
   */
  async getUnreadNotifications(): Promise<NotificationListResponse> {
    const client = await waitForApiClient();
    const response = await client.get('/notifications/unread');
    return response.data;
  },

  /**
   * Mark a notification as read
   */
  async markAsRead(notificationId: number): Promise<void> {
    const client = await waitForApiClient();
    await client.put(`/notifications/${notificationId}/read`);
  },

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<{ message: string; updated_count: number }> {
    const client = await waitForApiClient();
    const response = await client.put('/notifications/read-all');
    return response.data;
  },

  /**
   * Get unread notification count
   */
  async getUnreadCount(): Promise<{ unread_count: number }> {
    const client = await waitForApiClient();
    const response = await client.get('/notifications/unread-count');
    return response.data;
  },
};
