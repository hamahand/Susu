import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { Text, Portal, Modal } from 'react-native-paper';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { colors, spacing, typography, borderRadius } from '../theme';
import { groupService } from '../api/groupService';

type JoinGroupScreenProps = {
  navigation: any;
  route?: any;
};

export const JoinGroupScreen: React.FC<JoinGroupScreenProps> = ({ navigation, route }) => {
  const [groupCode, setGroupCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [joinedInfo, setJoinedInfo] = useState<{ group_id: number; rotation_position: number } | null>(null);
  const [error, setError] = useState('');

  const handleJoin = async () => {
    if (!groupCode || groupCode.length < 4) {
      setError('Please enter a valid group code');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const result = await groupService.joinGroup({ group_code: groupCode.toUpperCase() });
      setJoinedInfo(result);
      setSuccess(true);
    } catch (error: any) {
      setError(error.message || 'Failed to join group');
      Alert.alert('Error', error.message || 'Failed to join group');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDashboard = () => {
    setSuccess(false);
    if (joinedInfo) {
      navigation.navigate('GroupDashboard', { groupId: joinedInfo.group_id });
    }
  };

  const handleBackToGroups = () => {
    setSuccess(false);
    navigation.navigate('MyGroups');
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Join a Group</Text>
        <Text style={styles.subtitle}>Enter the group code shared by the admin</Text>

        <View style={styles.form}>
          <Input
            label="Group Code"
            value={groupCode}
            onChangeText={(text) => {
              setGroupCode(text.toUpperCase());
              setError('');
            }}
            placeholder="SUSU1234"
            autoCapitalize="characters"
            maxLength={8}
            error={error}
          />

          <Card style={styles.infoCard}>
            <Text style={styles.infoTitle}>💡 How to Join</Text>
            <Text style={styles.infoText}>
              1. Get the group code from the admin
            </Text>
            <Text style={styles.infoText}>
              2. Enter the code above
            </Text>
            <Text style={styles.infoText}>
              3. You'll be assigned a rotation position
            </Text>
            <Text style={styles.infoText}>
              4. Start contributing when payments begin!
            </Text>
          </Card>

          <Button onPress={handleJoin} loading={loading} mode="contained">
            Join Group
          </Button>

          <Button onPress={() => navigation.goBack()} mode="outlined">
            Cancel
          </Button>
        </View>
      </ScrollView>

      {/* Success Modal */}
      <Portal>
        <Modal
          visible={success}
          onDismiss={() => setSuccess(false)}
          contentContainerStyle={styles.modal}
        >
          <Text style={styles.modalTitle}>Successfully Joined! 🎉</Text>
          <Text style={styles.modalText}>
            You have been added to the group at position {joinedInfo?.rotation_position}
          </Text>

          <View style={styles.modalButtons}>
            <Button onPress={handleViewDashboard} mode="contained">
              View Group Dashboard
            </Button>
            <Button onPress={handleBackToGroups} mode="outlined">
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
    justifyContent: 'center',
  },
  title: {
    ...typography.h1,
    color: colors.primary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
  form: {
    gap: spacing.md,
  },
  infoCard: {
    backgroundColor: colors.primary + '10',
    marginVertical: spacing.md,
  },
  infoTitle: {
    ...typography.h3,
    color: colors.primary,
    marginBottom: spacing.md,
  },
  infoText: {
    ...typography.body,
    color: colors.text,
    marginBottom: spacing.sm,
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
    marginBottom: spacing.xl,
  },
  modalButtons: {
    gap: spacing.md,
  },
});

