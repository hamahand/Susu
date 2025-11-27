import apiClient from './client';
import { Payout } from '../types/api';

export const payoutService = {
  /**
   * Get current pending payout for a group
   */
  async getCurrentPayout(groupId: number): Promise<Payout> {
    const response = await apiClient.get<Payout>(`/payouts/group/${groupId}/current`);
    return response.data;
  },

  /**
   * Approve a payout (admin only)
   */
  async approvePayout(payoutId: number): Promise<{ message: string }> {
    const response = await apiClient.post(`/payouts/${payoutId}/approve`);
    return response.data;
  },

  /**
   * Get payout history for a group
   */
  async getGroupPayouts(groupId: number): Promise<Payout[]> {
    const response = await apiClient.get<Payout[]>(`/payouts/group/${groupId}`);
    return response.data;
  },
};

