import apiClient from './client';
import { Payout } from '../types/api';

export const payoutService = {
  /**
   * Get current payout for a group
   */
  async getCurrentPayout(groupId: number): Promise<Payout> {
    const response = await apiClient.get<Payout>(`/payouts/${groupId}/current`);
    return response.data;
  },

  /**
   * Approve a payout (admin only)
   */
  async approvePayout(payoutId: number): Promise<Payout> {
    const response = await apiClient.post<Payout>(`/payouts/${payoutId}/approve`);
    return response.data;
  },
};

