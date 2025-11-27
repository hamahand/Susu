import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { Text } from 'react-native-paper';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { colors, spacing, typography } from '../theme';
import { useAuth } from '../store/authContext';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { AuthStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<AuthStackParamList, 'OtpVerify'>;

export const OtpVerifyScreen: React.FC<Props> = ({ route }) => {
  const { phoneNumber } = route.params;
  const { loginWithOtp, requestOtp } = useAuth();
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleVerify = async () => {
    if (!code || code.length < 4) {
      setError('Please enter a valid verification code');
      return;
    }

    setLoading(true);
    setError('');
    try {
      await loginWithOtp(phoneNumber, code);
    } catch (e: any) {
      // Extract proper error message from error object
      let errorMessage = 'Invalid or expired code';
      
      if (e?.message) {
        errorMessage = e.message;
      } else if (e?.response?.data?.detail) {
        errorMessage = e.response.data.detail;
      } else if (typeof e === 'string') {
        errorMessage = e;
      } else if (e?.toString) {
        errorMessage = e.toString();
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError('');
    try {
      await requestOtp(phoneNumber);
      Alert.alert('Code sent', 'A new code has been sent to your phone.');
    } catch (e: any) {
      // Extract proper error message from error object
      let errorMessage = 'Could not resend code';
      
      if (e?.message) {
        errorMessage = e.message;
      } else if (e?.response?.data?.detail) {
        errorMessage = e.response.data.detail;
      } else if (typeof e === 'string') {
        errorMessage = e;
      } else if (e?.toString) {
        errorMessage = e.toString();
      }
      
      setError(errorMessage);
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Enter Verification Code</Text>
        <Text style={styles.subtitle}>We sent an SMS code to {phoneNumber}</Text>

        {error ? (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : null}

        <Input
          label="6-digit Code"
          value={code}
          onChangeText={setCode}
          placeholder="123456"
          keyboardType="number-pad"
        />

        <Button onPress={handleVerify} loading={loading} mode="contained">Verify</Button>
        <Button onPress={handleResend} mode="text">Resend Code</Button>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { flex: 1, padding: spacing.lg, justifyContent: 'center' },
  title: { ...typography.h1, color: colors.primary, marginBottom: spacing.sm },
  subtitle: { ...typography.body, color: colors.textSecondary, marginBottom: spacing.lg },
  errorContainer: {
    backgroundColor: '#fee2e2',
    borderColor: '#fca5a5',
    borderWidth: 1,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  errorText: {
    color: '#dc2626',
    fontSize: 14,
    textAlign: 'center',
    fontWeight: '500',
  },
});


