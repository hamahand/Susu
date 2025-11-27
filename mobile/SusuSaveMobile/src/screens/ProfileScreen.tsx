import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert, Modal } from 'react-native';
import { Text, List, Divider } from 'react-native-paper';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { PaymentMethodSelector, PaymentMethod } from '../components/PaymentMethodSelector';
import { colors, spacing, typography } from '../theme';
import { useAuth } from '../store/authContext';
import { Input } from '../components/Input';
import { groupService } from '../api/groupService';
import { paymentService } from '../api/paymentService';
import { config } from '../config';

export const ProfileScreen: React.FC = () => {
  const { user, logout, updateProfile } = useAuth();
  const [stats, setStats] = useState({
    totalGroups: 0,
    totalContributions: 0,
    totalPayments: 0,
  });
  const [username, setUsername] = useState(user?.name || '');
  const [email, setEmail] = useState((user as any)?.email || '');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('manual');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    try {
      setSaving(true);
      await updateProfile({ username, email });
      Alert.alert('Saved', 'Profile updated');
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const groups = await groupService.getMyGroups();
      const payments = await paymentService.getPaymentHistory();
      
      const successfulPayments = payments.filter(p => p.status === 'success');
      const totalAmount = successfulPayments.reduce((sum, p) => sum + p.amount, 0);

      setStats({
        totalGroups: groups.length,
        totalContributions: totalAmount,
        totalPayments: successfulPayments.length,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Logout',
        style: 'destructive',
        onPress: logout,
      },
    ]);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* User Info Card */}
      <Card>
        <View style={styles.avatarContainer}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </Text>
          </View>
        </View>
        <Input label="Username" value={username} onChangeText={setUsername} />
        <Input label="Email (optional)" value={email} onChangeText={setEmail} keyboardType="email-address" />
        <Button onPress={handleSave} loading={saving} mode="contained">Save Profile</Button>
        <Text style={styles.userPhone}>{user?.phone_number || ''}</Text>
      </Card>

      {/* Statistics Card */}
      <Card>
        <Text style={styles.sectionTitle}>Statistics</Text>
        <Divider style={styles.divider} />
        
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Groups Joined</Text>
          <Text style={styles.statValue}>{stats.totalGroups}</Text>
        </View>
        
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Total Contributions</Text>
          <Text style={styles.statValue}>GHS {stats.totalContributions.toFixed(2)}</Text>
        </View>
        
        <View style={styles.statRow}>
          <Text style={styles.statLabel}>Payments Made</Text>
          <Text style={styles.statValue}>{stats.totalPayments}</Text>
        </View>
      </Card>

      {/* Payment Settings Card */}
      <Card>
        <Text style={styles.sectionTitle}>Payment Settings</Text>
        <Divider style={styles.divider} />
        
        <List.Item
          title="Payment Method"
          description={`Current: ${paymentMethod.toUpperCase()}`}
          left={props => <List.Icon {...props} icon="credit-card" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => setShowPaymentModal(true)}
        />
        
        <List.Item
          title="Payment Reminders"
          description="Receive SMS reminders for payments"
          left={props => <List.Icon {...props} icon="bell" />}
          right={props => <List.Icon {...props} icon="check" color={colors.success} />}
        />
      </Card>

      {/* Settings Card */}
      <Card>
        <Text style={styles.sectionTitle}>About</Text>
        <Divider style={styles.divider} />
        
        <List.Item
          title="App Version"
          description={config.APP_VERSION}
          left={props => <List.Icon {...props} icon="information" />}
        />
        
        <List.Item
          title="Privacy Policy"
          description="View our privacy policy"
          left={props => <List.Icon {...props} icon="shield-check" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => Alert.alert('Info', 'Privacy policy coming soon')}
        />
        
        <List.Item
          title="Terms of Service"
          description="View terms and conditions"
          left={props => <List.Icon {...props} icon="file-document" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => Alert.alert('Info', 'Terms of service coming soon')}
        />
      </Card>

      {/* Payment Method Modal */}
      <Modal
        visible={showPaymentModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowPaymentModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Change Payment Method</Text>
            
            <PaymentMethodSelector
              selected={paymentMethod}
              onSelect={(method) => {
                setPaymentMethod(method);
                Alert.alert(
                  'Payment Method Updated',
                  `Your payment method has been changed to ${method.toUpperCase()}. Changes will take effect for future payments.`
                );
                setShowPaymentModal(false);
              }}
            />
            
            <View style={styles.modalButtons}>
              <Button
                mode="outlined"
                onPress={() => setShowPaymentModal(false)}
              >
                Cancel
              </Button>
            </View>
          </View>
        </View>
      </Modal>

      {/* Logout Button */}
      <Button onPress={handleLogout} mode="outlined" style={styles.logoutButton}>
        Logout
      </Button>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.md,
  },
  avatarContainer: {
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 36,
    color: colors.surface,
    fontWeight: 'bold',
  },
  userName: {
    ...typography.h2,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  userPhone: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  divider: {
    marginBottom: spacing.md,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  statLabel: {
    ...typography.body,
    color: colors.text,
  },
  statValue: {
    ...typography.body,
    color: colors.primary,
    fontWeight: '600',
  },
  logoutButton: {
    marginTop: spacing.lg,
    marginBottom: spacing.xl,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: spacing.lg,
    maxHeight: '80%',
  },
  modalTitle: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  modalButtons: {
    marginTop: spacing.lg,
    gap: spacing.md,
  },
});

