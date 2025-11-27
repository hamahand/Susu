import React, { useState } from 'react';
import { Alert, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { paymentService } from '../api/paymentService';

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
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    try {
      setLoading(true);

      if (isCurrentUser && paymentId) {
        // User pays their own payment
        await paymentService.payNow(paymentId);
        Alert.alert(
          'Payment Request Sent',
          'Check your phone for MoMo prompt to approve the payment.',
          [{ text: 'OK', onPress: onSuccess }]
        );
      } else if (isAdmin) {
        // Admin requests payment from member
        Alert.alert(
          'Request Payment',
          `Request payment of GHS ${amount.toFixed(2)} from ${memberName}?`,
          [
            { text: 'Cancel', style: 'cancel' },
            {
              text: 'Send Request',
              onPress: async () => {
                try {
                  await paymentService.adminRequestPayment({
                    group_id: groupId,
                    user_id: userId,
                    round_number: roundNumber,
                  });
                  Alert.alert(
                    'Payment Request Sent',
                    `${memberName} will receive a MoMo prompt on their phone to approve the payment.`,
                    [{ text: 'OK', onPress: onSuccess }]
                  );
                } catch (error: any) {
                  Alert.alert(
                    'Error',
                    error.response?.data?.detail || 'Failed to send payment request'
                  );
                }
              },
            },
          ]
        );
      }
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Failed to initiate payment'
      );
    } finally {
      setLoading(false);
    }
  };

  // Don't render button if not applicable
  if (!isCurrentUser && !isAdmin) {
    return null;
  }

  return (
    <TouchableOpacity
      onPress={handlePayment}
      disabled={loading}
      style={[
        styles.button,
        isAdmin && !isCurrentUser ? styles.adminButton : styles.userButton,
        loading && styles.loadingButton
      ]}
    >
      <Text style={[
        styles.buttonText,
        isAdmin && !isCurrentUser ? styles.adminButtonText : styles.userButtonText
      ]}>
        {loading ? '⏳' : (isCurrentUser ? '💳 Pay Now' : '📱 Request Payment')}
      </Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    marginTop: 8,
    width: '100%',
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  userButton: {
    backgroundColor: '#4CAF50',
  },
  adminButton: {
    backgroundColor: '#FFFFFF',
    borderColor: '#2196F3',
    borderWidth: 2,
  },
  loadingButton: {
    opacity: 0.7,
  },
  buttonText: {
    fontSize: 13,
    fontWeight: '600',
    textAlign: 'center',
  },
  userButtonText: {
    color: '#FFFFFF',
  },
  adminButtonText: {
    color: '#2196F3',
  },
});

