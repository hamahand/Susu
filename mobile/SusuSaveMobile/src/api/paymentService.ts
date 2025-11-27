import apiClient from './client';
import { Payment, TriggerPaymentRequest, UnpaidPayment } from '../types/api';

interface AdminPaymentRequest {
  group_id: number;
  user_id: number;
  round_number: number;
}

interface PaymentStatusResponse {
  payment_id: number;
  status: string;
  mtn_status?: string;
  amount: number;
  transaction_id?: string;
  financial_transaction_id?: string;
}

export const paymentService = {
  /**
   * Get payment history for current user
   */
  async getPaymentHistory(): Promise<Payment[]> {
    const response = await apiClient.get<Payment[]>('/payments/history');
    return response.data;
  },

  /**
   * Manually trigger a payment
   */
  async triggerPayment(data: TriggerPaymentRequest): Promise<Payment> {
    const response = await apiClient.post<Payment>('/payments/manual-trigger', data);
    return response.data;
  },

  /**
   * Retry a failed payment
   */
  async retryPayment(paymentId: number): Promise<Payment> {
    const response = await apiClient.post<Payment>(`/payments/${paymentId}/retry`);
    return response.data;
  },

  /**
   * Get unpaid payment for a group
   */
  async getUnpaidPayment(groupId: number): Promise<UnpaidPayment> {
    const response = await apiClient.get<UnpaidPayment>(`/groups/${groupId}/unpaid-payment`);
    return response.data;
  },

  /**
   * Pay now - trigger manual payment for user's own contribution
   */
  async payNow(paymentId: number): Promise<Payment> {
    const response = await apiClient.post<Payment>(`/payments/${paymentId}/pay-now`);
    return response.data;
  },

  /**
   * Admin requests payment from a member (NEW)
   * Sends MoMo payment request to member's phone
   */
  async adminRequestPayment(data: AdminPaymentRequest): Promise<Payment> {
    const response = await apiClient.post<Payment>('/payments/admin/request-payment', data);
    return response.data;
  },

  /**
   * Check payment status (NEW)
   * Returns both local and MTN transaction status
   */
  async checkPaymentStatus(paymentId: number): Promise<PaymentStatusResponse> {
    const response = await apiClient.get<PaymentStatusResponse>(`/payments/${paymentId}/status`);
    return response.data;
  },

  /**
   * Mark payment as cash paid (admin only)
   */
  async markAsPaid(paymentId: number): Promise<Payment> {
    const response = await apiClient.post<Payment>(`/payments/${paymentId}/mark-paid`, {});
    return response.data;
  },
};

