import apiClient from './client';
import { Payment, TriggerPaymentRequest } from '../types/api';

export const paymentService = {
  /**
   * Trigger payment for a group
   */
  async triggerPayment(data: TriggerPaymentRequest): Promise<{ message: string }> {
    const response = await apiClient.post('/payments/trigger', data);
    return response.data;
  },

  /**
   * Get payment history for a group
   */
  async getGroupPayments(groupId: number): Promise<Payment[]> {
    const response = await apiClient.get<Payment[]>(`/payments/group/${groupId}`);
    return response.data;
  },

  /**
   * Get user's payment history
   */
  async getMyPayments(): Promise<Payment[]> {
    const response = await apiClient.get<Payment[]>('/payments/my-payments');
    return response.data;
  },
};

