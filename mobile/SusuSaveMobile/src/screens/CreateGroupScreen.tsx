import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, Alert, Share } from 'react-native';
import { Text, Portal, Modal, Switch } from 'react-native-paper';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { colors, spacing, typography, borderRadius } from '../theme';
import { groupService } from '../api/groupService';
import { Group } from '../types/api';
import * as Clipboard from 'expo-clipboard';

export const CreateGroupScreen: React.FC<any> = ({ navigation }) => {
  const [name, setName] = useState('');
  const [amount, setAmount] = useState('');
  const [numMembers, setNumMembers] = useState('');
  const [frequency, setFrequency] = useState<'weekly' | 'biweekly' | 'monthly'>('weekly');
  const [cashOnly, setCashOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [createdGroup, setCreatedGroup] = useState<Group | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [errors, setErrors] = useState<{
    name?: string;
    amount?: string;
    numMembers?: string;
  }>({});

  const validate = () => {
    const newErrors: any = {};

    if (!name || name.length < 3) {
      newErrors.name = 'Group name must be at least 3 characters';
    }

    const amountNum = parseFloat(amount);
    if (!amount || isNaN(amountNum) || amountNum <= 0) {
      newErrors.amount = 'Amount must be greater than 0';
    }

    const membersNum = parseInt(numMembers);
    if (!numMembers || isNaN(membersNum) || membersNum < 2 || membersNum > 50) {
      newErrors.numMembers = 'Number of members must be between 2 and 50';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreate = async () => {
    if (!validate()) return;

    setLoading(true);
    setErrors({});
    try {
      // Number of cycles = number of members (each member gets payout once)
      const group = await groupService.createGroup({
        name,
        contribution_amount: parseFloat(amount),
        num_cycles: parseInt(numMembers),
        cash_only: cashOnly,
      });

      // Successfully created - show modal
      setCreatedGroup(group);
      setModalVisible(true);
    } catch (error: any) {
      console.error('Create group error:', error);
      const errorMsg = error.message || 'Failed to create group';
      
      // Check if it's a network/serialization error but group might be created
      if (errorMsg.includes('JSON') || errorMsg.includes('unexpected')) {
        Alert.alert(
          'Group May Be Created',
          'There was an error reading the response, but your group may have been created. Check "My Groups" to verify.',
          [{ text: 'OK', onPress: () => navigation.navigate('MyGroups') }]
        );
      } else {
        Alert.alert('Error Creating Group', errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = async () => {
    if (createdGroup) {
      await Clipboard.setStringAsync(createdGroup.group_code);
      Alert.alert('Copied', 'Group code copied to clipboard');
    }
  };

  const handleShare = async () => {
    if (createdGroup) {
      try {
        await Share.share({
          message: `Join my SusuSave group "${createdGroup.name}"! Use code: ${createdGroup.group_code}`,
        });
      } catch (error) {
        console.error('Share error:', error);
      }
    }
  };

  const handleViewDashboard = () => {
    setModalVisible(false);
    // Reset form
    setName('');
    setAmount('');
    setNumMembers('');
    if (createdGroup) {
      navigation.navigate('GroupDashboard', { groupId: createdGroup.id });
    }
  };

  const handleBackToGroups = () => {
    setModalVisible(false);
    // Reset form
    setName('');
    setAmount('');
    setNumMembers('');
    setCreatedGroup(null);
    navigation.navigate('MyGroups');
  };

  const totalAmount = amount && numMembers ? parseFloat(amount) * parseInt(numMembers) : 0;
  const frequencyText = frequency === 'weekly' ? 'week' : frequency === 'biweekly' ? '2 weeks' : 'month';

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Create New Group</Text>

        <View style={styles.form}>
          <Input
            label="Group Name"
            value={name}
            onChangeText={setName}
            placeholder="e.g., Weekly Savings Circle"
            error={errors.name}
          />

          <Input
            label="Contribution Amount (GHS)"
            value={amount}
            onChangeText={setAmount}
            placeholder="50"
            keyboardType="numeric"
            error={errors.amount}
          />

          <View>
            <Text style={styles.label}>Contribution Frequency</Text>
            <View style={styles.frequencyButtons}>
              <Button
                onPress={() => setFrequency('weekly')}
                mode={frequency === 'weekly' ? 'contained' : 'outlined'}
                style={styles.freqButton}
              >
                Weekly
              </Button>
              <Button
                onPress={() => setFrequency('biweekly')}
                mode={frequency === 'biweekly' ? 'contained' : 'outlined'}
                style={styles.freqButton}
              >
                Bi-weekly
              </Button>
              <Button
                onPress={() => setFrequency('monthly')}
                mode={frequency === 'monthly' ? 'contained' : 'outlined'}
                style={styles.freqButton}
              >
                Monthly
              </Button>
            </View>
          </View>

          <Input
            label="Number of Members"
            value={numMembers}
            onChangeText={setNumMembers}
            placeholder="5"
            keyboardType="numeric"
            error={errors.numMembers}
          />

          {/* Cash Only Toggle */}
          <View style={styles.cashOnlyContainer}>
            <View style={styles.cashOnlyText}>
              <Text style={styles.label}>Cash Only Group</Text>
              <Text style={styles.cashOnlyDescription}>
                {cashOnly 
                  ? 'Members pay cash. Admins mark payments as received.' 
                  : 'Payments processed via mobile money automatically.'}
              </Text>
            </View>
            <Switch
              value={cashOnly}
              onValueChange={setCashOnly}
              color={colors.primary}
            />
          </View>

          {/* Preview Card */}
          {amount && numMembers && (
            <Card style={styles.previewCard}>
              <Text style={styles.previewTitle}>Preview</Text>
              <View style={styles.previewRow}>
                <Text style={styles.previewLabel}>Contribution:</Text>
                <Text style={styles.previewValue}>GHS {amount} / {frequencyText}</Text>
              </View>
              <View style={styles.previewRow}>
                <Text style={styles.previewLabel}>Members:</Text>
                <Text style={styles.previewValue}>{numMembers} people</Text>
              </View>
              <View style={styles.previewRow}>
                <Text style={styles.previewLabel}>Rounds:</Text>
                <Text style={styles.previewValue}>{numMembers} (one payout per member)</Text>
              </View>
              <View style={[styles.previewRow, styles.previewTotal]}>
                <Text style={styles.previewLabel}>Total payout per member:</Text>
                <Text style={[styles.previewValue, styles.totalValue]}>
                  GHS {totalAmount.toFixed(2)}
                </Text>
              </View>
            </Card>
          )}

          <Button onPress={handleCreate} loading={loading} mode="contained">
            Create Group
          </Button>
        </View>
      </ScrollView>

      {/* Success Modal */}
      <Portal>
        <Modal
          visible={modalVisible}
          onDismiss={() => setModalVisible(false)}
          contentContainerStyle={styles.modal}
        >
          <Text style={styles.modalTitle}>Group Created! 🎉</Text>
          <Text style={styles.modalText}>
            Share this code with {numMembers ? parseInt(numMembers) - 1 : 'your'} members to join:
          </Text>

          <View style={styles.codeContainer}>
            <Text style={styles.groupCode}>{createdGroup?.group_code}</Text>
          </View>

          <Card style={styles.summaryCard}>
            <Text style={styles.summaryText}>📅 {frequencyText.charAt(0).toUpperCase() + frequencyText.slice(1)} contributions</Text>
            <Text style={styles.summaryText}>💰 GHS {amount} per contribution</Text>
            <Text style={styles.summaryText}>👥 {numMembers} members total</Text>
            <Text style={styles.summaryText}>🔄 {numMembers} rounds (each member receives once)</Text>
            <Text style={styles.summaryText}>
              {cashOnly ? '💵 Cash payments (no mobile money)' : '📱 Mobile money payments'}
            </Text>
          </Card>

          <View style={styles.modalButtons}>
            <Button onPress={handleCopyCode} mode="outlined">
              Copy Code
            </Button>
            <Button onPress={handleShare} mode="outlined">
              Share
            </Button>
            <Button onPress={handleViewDashboard} mode="contained">
              View Dashboard
            </Button>
            <Button onPress={handleBackToGroups} mode="text">
              Back to My Groups
            </Button>
          </View>
        </Modal>
      </Portal>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    padding: spacing.lg,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.xl,
  },
  form: {
    gap: spacing.md,
  },
  label: {
    ...typography.body,
    color: colors.text,
    marginBottom: spacing.sm,
    fontWeight: '600',
  },
  frequencyButtons: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  freqButton: {
    flex: 1,
  },
  previewCard: {
    backgroundColor: colors.primary + '10',
    marginTop: spacing.md,
  },
  previewTitle: {
    ...typography.h3,
    color: colors.primary,
    marginBottom: spacing.md,
  },
  previewRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  previewLabel: {
    ...typography.body,
    color: colors.text,
  },
  previewValue: {
    ...typography.body,
    color: colors.text,
    fontWeight: '600',
  },
  previewTotal: {
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.sm,
    marginTop: spacing.sm,
  },
  totalValue: {
    color: colors.primary,
    fontSize: 18,
  },
  cashOnlyContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cashOnlyText: {
    flex: 1,
    marginRight: spacing.md,
  },
  cashOnlyDescription: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  modal: {
    backgroundColor: colors.surface,
    padding: spacing.xl,
    margin: spacing.lg,
    borderRadius: borderRadius.lg,
  },
  modalTitle: {
    ...typography.h2,
    color: colors.primary,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  modalText: {
    ...typography.body,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  codeContainer: {
    backgroundColor: colors.background,
    padding: spacing.lg,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  groupCode: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.primary,
    letterSpacing: 4,
  },
  summaryCard: {
    backgroundColor: colors.background,
    marginBottom: spacing.xl,
  },
  summaryText: {
    ...typography.body,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  modalButtons: {
    gap: spacing.md,
  },
});

