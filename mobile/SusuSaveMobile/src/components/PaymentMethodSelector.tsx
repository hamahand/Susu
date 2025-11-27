import React from 'react';
import { View, TouchableOpacity, StyleSheet } from 'react-native';
import { Text } from 'react-native-paper';
import { colors, spacing, typography } from '../theme';

export type PaymentMethod = 'auto' | 'manual' | 'ussd';

interface PaymentMethodOption {
  id: PaymentMethod;
  icon: string;
  title: string;
  description: string;
  badge?: string;
  recommended?: boolean;
}

interface PaymentMethodSelectorProps {
  selected: PaymentMethod;
  onSelect: (method: PaymentMethod) => void;
}

export const PaymentMethodSelector: React.FC<PaymentMethodSelectorProps> = ({
  selected,
  onSelect,
}) => {
  const methods: PaymentMethodOption[] = [
    {
      id: 'auto',
      icon: '🤖',
      title: 'Automated',
      description: 'Set it and forget it! Monthly reminders sent automatically.',
      badge: 'Recommended',
      recommended: true,
    },
    {
      id: 'manual',
      icon: '👤',
      title: 'Manual Approval',
      description: 'Review and approve each payment in your MTN MoMo app.',
    },
    {
      id: 'ussd',
      icon: '📱',
      title: 'USSD Payment',
      description: 'Pay via *920*55# when you receive SMS reminders.',
    },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.label}>Choose Payment Method</Text>
        <Text style={styles.helperText}>
          Select how you'd like to make your susu contributions
        </Text>
      </View>

      <View style={styles.optionsContainer}>
        {methods.map((method) => (
          <TouchableOpacity
            key={method.id}
            style={[
              styles.option,
              selected === method.id && styles.optionSelected,
            ]}
            onPress={() => onSelect(method.id)}
            activeOpacity={0.7}
          >
            {/* Badge for recommended */}
            {method.badge && (
              <View style={styles.badgeContainer}>
                <Text style={styles.badgeText}>{method.badge}</Text>
              </View>
            )}

            {/* Icon */}
            <Text style={styles.icon}>{method.icon}</Text>

            {/* Content */}
            <View style={styles.content}>
              <Text style={styles.methodTitle}>{method.title}</Text>
              <Text style={styles.methodDescription}>{method.description}</Text>
            </View>

            {/* Selection indicator */}
            <View style={styles.radioContainer}>
              <View style={[
                styles.radioOuter,
                selected === method.id && styles.radioOuterSelected,
              ]}>
                {selected === method.id && (
                  <View style={styles.radioInner} />
                )}
              </View>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      {/* Additional info based on selection */}
      {selected === 'auto' && (
        <View style={styles.infoBox}>
          <Text style={styles.infoIcon}>ℹ️</Text>
          <Text style={styles.infoText}>
            You'll receive a MoMo prompt each month. Simply approve on your phone - it takes just 5 seconds!
          </Text>
        </View>
      )}

      {selected === 'manual' && (
        <View style={styles.infoBox}>
          <Text style={styles.infoIcon}>ℹ️</Text>
          <Text style={styles.infoText}>
            You'll receive a notification in your MTN MoMo app to review and approve each payment.
          </Text>
        </View>
      )}

      {selected === 'ussd' && (
        <View style={styles.infoBox}>
          <Text style={styles.infoIcon}>ℹ️</Text>
          <Text style={styles.infoText}>
            You'll receive an SMS reminder with instructions to dial *920*55# and complete payment via USSD.
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: spacing.md,
  },
  header: {
    marginBottom: spacing.md,
  },
  label: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  helperText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  optionsContainer: {
    gap: spacing.md,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: colors.border,
    position: 'relative',
  },
  optionSelected: {
    borderColor: colors.primary,
    backgroundColor: `${colors.primary}10`,
  },
  badgeContainer: {
    position: 'absolute',
    top: -8,
    right: 12,
    backgroundColor: colors.success,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    ...typography.caption,
    color: colors.white,
    fontWeight: '700',
    fontSize: 10,
  },
  icon: {
    fontSize: 32,
    marginRight: spacing.md,
  },
  content: {
    flex: 1,
  },
  methodTitle: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  methodDescription: {
    ...typography.caption,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  radioContainer: {
    marginLeft: spacing.sm,
  },
  radioOuter: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  radioOuterSelected: {
    borderColor: colors.primary,
  },
  radioInner: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.primary,
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginTop: spacing.md,
    padding: spacing.md,
    backgroundColor: `${colors.info}15`,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: colors.info,
  },
  infoIcon: {
    fontSize: 16,
    marginRight: spacing.sm,
    marginTop: 2,
  },
  infoText: {
    ...typography.caption,
    color: colors.text,
    flex: 1,
    lineHeight: 18,
  },
});

