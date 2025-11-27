import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { PaymentStatus, PayoutStatus } from '../types/api';

interface StatusBadgeProps {
  status: PaymentStatus | PayoutStatus | 'paid' | 'unpaid';
  size?: 'small' | 'medium';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'small' }) => {
  const getColors = () => {
    switch (status) {
      case 'success':
      case 'paid':
        return {
          backgroundColor: '#E8F5E8',
          textColor: '#2E7D32',
          borderColor: '#4CAF50',
        };
      case 'pending':
        return {
          backgroundColor: '#FFF3E0',
          textColor: '#F57C00',
          borderColor: '#FF9800',
        };
      case 'failed':
        return {
          backgroundColor: '#FFEBEE',
          textColor: '#D32F2F',
          borderColor: '#F44336',
        };
      case 'unpaid':
        return {
          backgroundColor: '#F5F5F5',
          textColor: '#666666',
          borderColor: '#BDBDBD',
        };
      default:
        return {
          backgroundColor: '#E3F2FD',
          textColor: '#1976D2',
          borderColor: '#2196F3',
        };
    }
  };

  const getLabel = () => {
    if (typeof status === 'string') {
      return status.charAt(0).toUpperCase() + status.slice(1);
    }
    return status;
  };

  const colors = getColors();
  const fontSize = size === 'small' ? 11 : 13;
  const padding = size === 'small' ? 6 : 8;

  return (
    <View style={[
      styles.badge,
      {
        backgroundColor: colors.backgroundColor,
        borderColor: colors.borderColor,
        paddingHorizontal: padding,
        paddingVertical: padding - 2,
      }
    ]}>
      <Text style={[
        styles.badgeText,
        {
          color: colors.textColor,
          fontSize: fontSize,
        }
      ]}>
        {getLabel()}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    borderRadius: 12,
    borderWidth: 1,
    alignSelf: 'flex-start',
  },
  badgeText: {
    fontWeight: '600',
    textAlign: 'center',
  },
});

