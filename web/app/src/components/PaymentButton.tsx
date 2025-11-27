import React, { useState } from 'react';
import { Button } from './Button';
import apiClient from '../api/client';

interface PaymentButtonProps {
  paymentId?: number;
  groupId: number;
  userId: number;
  roundNumber: number;
  amount: number;
  memberName?: string;
  isAdmin?: boolean;
  isCurrentUser?: boolean;
  onSuccess?: () => void;
}

export const PaymentButton: React.FC<PaymentButtonProps> = ({
  paymentId,
  groupId,
  userId,
  roundNumber,
  amount,
  memberName = 'member',
  isAdmin = false,
  isCurrentUser = false,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    setLoading(true);
    try {
      let result;
      
      if (isCurrentUser && paymentId) {
        // User pays their own payment
        result = await apiClient.post(`/payments/${paymentId}/pay-now`);
        alert('Payment request sent! Check your phone for MoMo prompt.');
      } else if (isAdmin) {
        // Admin requests payment from member
        if (!confirm(`Request payment of GHS ${amount.toFixed(2)} from ${memberName}?`)) {
          setLoading(false);
          return;
        }
        
        result = await apiClient.post('/payments/admin/request-payment', {
          group_id: groupId,
          user_id: userId,
          round_number: roundNumber
        });
        alert(`Payment request sent to ${memberName}! They will receive a MoMo prompt.`);
      }
      
      // Refresh parent component
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to initiate payment';
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Don't render button if not applicable
  if (!isCurrentUser && !isAdmin) {
    return null;
  }

  return (
    <Button
      onClick={handlePayment}
      loading={loading}
      size="small"
      variant={isAdmin && !isCurrentUser ? "outline" : "primary"}
      disabled={loading}
    >
      {isCurrentUser ? '💳 Pay Now' : '📱 Request Payment'}
    </Button>
  );
};

