import React from 'react';
import { Button as PaperButton, ActivityIndicator } from 'react-native-paper';
import { StyleSheet } from 'react-native';
import { colors, spacing } from '../theme';

interface ButtonProps {
  children: string;
  onPress: () => void;
  mode?: 'contained' | 'outlined' | 'text';
  loading?: boolean;
  disabled?: boolean;
  icon?: string;
  style?: any;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onPress,
  mode = 'contained',
  loading = false,
  disabled = false,
  icon,
  style,
}) => {
  return (
    <PaperButton
      mode={mode}
      onPress={onPress}
      disabled={disabled || loading}
      icon={icon}
      loading={loading}
      style={[styles.button, style]}
      contentStyle={styles.content}
      labelStyle={styles.label}
    >
      {children}
    </PaperButton>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: 8,
  },
  content: {
    paddingVertical: spacing.xs,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
  },
});

