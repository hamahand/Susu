import React, { useState, useEffect, useCallback } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl, Alert, Modal, TextInput, TouchableOpacity } from 'react-native';
import { Text, Appbar, Divider } from 'react-native-paper';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { PaymentButton } from '../components/PaymentButton';
import { colors, spacing, typography } from '../theme';
import { groupService } from '../api/groupService';
import { payoutService } from '../api/payoutService';
import { GroupDashboard } from '../types/api';
import * as Clipboard from 'expo-clipboard';
import { useFocusEffect } from '@react-navigation/native';
import { useAuth } from '../store/authContext';

export const GroupDashboardScreen: React.FC<any> = ({ route, navigation }) => {
  const { groupId } = route.params;
  const { user: currentUser } = useAuth();
  const [dashboard, setDashboard] = useState<GroupDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [approving, setApproving] = useState(false);
  const [inviteModalVisible, setInviteModalVisible] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [inviting, setInviting] = useState(false);
  const [pendingInvitations, setPendingInvitations] = useState<any[]>([]);
  const [showInvitations, setShowInvitations] = useState(false);

  const fetchDashboard = async () => {
    try {
      const data = await groupService.getGroupDashboard(groupId);
      setDashboard(data);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    loadPendingInvitations();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboard();
      loadPendingInvitations();
    }, 30000);
    return () => clearInterval(interval);
  }, [groupId]);

  // Refresh when screen comes into focus (e.g., after someone joins)
  useFocusEffect(
    useCallback(() => {
      fetchDashboard();
      loadPendingInvitations();
    }, [groupId])
  );

  const handleCopyCode = async () => {
    if (dashboard) {
      await Clipboard.setStringAsync(dashboard.group.group_code);
      Alert.alert('Copied', 'Group code copied to clipboard');
    }
  };

  const handleApprovePayout = async () => {
    if (!dashboard) return;

    try {
      const payout = await payoutService.getCurrentPayout(groupId);
      
      Alert.alert(
        'Approve Payout',
        `Approve payout of GHS ${payout.amount} to ${dashboard.next_recipient?.name}?`,
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Approve',
            onPress: async () => {
              setApproving(true);
              try {
                await payoutService.approvePayout(payout.id);
                Alert.alert('Success', 'Payout approved successfully!');
                fetchDashboard();
              } catch (error: any) {
                Alert.alert('Error', error.message || 'Failed to approve payout');
              } finally {
                setApproving(false);
              }
            },
          },
        ]
      );
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to load payout information');
    }
  };

  const handleInviteMember = async () => {
    if (!phoneNumber.trim()) {
      Alert.alert('Error', 'Please enter a phone number');
      return;
    }

    if (!phoneNumber.startsWith('+')) {
      Alert.alert('Error', 'Phone number must include country code (e.g., +233...)');
      return;
    }

    setInviting(true);
    try {
      await groupService.inviteMember(groupId, phoneNumber.trim());
      Alert.alert('Success', 'Invitation sent! They will receive an SMS with the group code.');
      setPhoneNumber('');
      setInviteModalVisible(false);
      loadPendingInvitations();
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to send invitation');
    } finally {
      setInviting(false);
    }
  };

  const loadPendingInvitations = async () => {
    try {
      const invitations = await groupService.getPendingInvitations(groupId);
      setPendingInvitations(invitations);
    } catch (error: any) {
      // Silently fail if not admin or error loading
      console.log('Could not load invitations:', error.message);
    }
  };

  const isAdmin = dashboard?.members.find(m => m.user_id === dashboard?.group.creator_id)?.is_admin;

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (!dashboard) {
    return (
      <View style={styles.container}>
        <Text>Dashboard not found</Text>
      </View>
    );
  }

  const { group, members, total_collected_current_round, next_recipient } = dashboard;
  const totalExpected = group.contribution_amount * members.length;
  const progress = totalExpected > 0 ? total_collected_current_round / totalExpected : 0;

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title={group.name} />
        <Appbar.Action icon="refresh" onPress={fetchDashboard} />
      </Appbar.Header>

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => {
            setRefreshing(true);
            fetchDashboard();
          }} />
        }
      >
        {/* Group Info Card */}
        <Card style={styles.groupInfoCard}>
          <View style={styles.headerRow}>
            <View style={styles.groupCodeContainer}>
              <Text style={styles.groupCodeLabel}>Group Code</Text>
              <Text style={styles.groupCode} onPress={handleCopyCode}>
                {group.group_code} 📋
              </Text>
            </View>
            <StatusBadge status={group.status as any} />
          </View>
          
          <View style={styles.roundInfoContainer}>
            <Text style={styles.roundInfo}>
              Round {group.current_round} of {group.num_cycles}
            </Text>
            <Text style={styles.contributionAmount}>
              GHS {group.contribution_amount} per member
            </Text>
          </View>
          
          {/* Invite Button (Admin Only) */}
          {members.some(m => m.is_admin) && (
            <>
              <Button
                onPress={() => setInviteModalVisible(true)}
                mode="contained"
                style={styles.inviteButton}
                buttonColor="#4CAF50"
                textColor="#FFFFFF"
              >
                📨 Invite Member
              </Button>
              <Button
                onPress={() => navigation.navigate('GroupSettings', { groupId })}
                mode="outlined"
                style={styles.settingsButton}
              >
                ⚙️ Group Settings
              </Button>
            </>
          )}
        </Card>

        {/* Pending Invitations (Admin Only) */}
        {members.some(m => m.is_admin) && pendingInvitations.length > 0 && (
          <Card>
            <View style={styles.headerRow}>
              <Text style={styles.sectionTitle}>Pending Invitations</Text>
              <Text style={styles.invitationCount}>({pendingInvitations.length})</Text>
            </View>
            <Divider style={styles.divider} />
            {pendingInvitations.map((inv) => (
              <View key={inv.id} style={styles.invitationRow}>
                <Text style={styles.invitationPhone}>{inv.phone_number}</Text>
                <Text style={styles.invitationDate}>
                  {new Date(inv.created_at).toLocaleDateString()}
                </Text>
              </View>
            ))}
          </Card>
        )}

        {/* Stats Cards */}
        <View style={styles.statsRow}>
          <Card style={styles.statCard}>
            <View style={styles.statContent}>
              <Text style={styles.statLabel}>Collected</Text>
              <Text style={styles.statValue}>
                GHS {total_collected_current_round.toFixed(2)}
              </Text>
              <Text style={styles.statSubtext}>of {totalExpected.toFixed(2)}</Text>
              <View style={styles.progressBar}>
                <View style={[styles.progressFill, { width: `${progress * 100}%` }]} />
              </View>
            </View>
          </Card>

          <Card style={styles.statCard}>
            <View style={styles.statContent}>
              <Text style={styles.statLabel}>Members Paid</Text>
              <Text style={styles.statValue}>
                {members.filter(m => m.paid_current_round).length} / {members.length}
              </Text>
              <Text style={styles.statSubtext}>{(progress * 100).toFixed(0)}% complete</Text>
              <View style={styles.progressBar}>
                <View style={[styles.progressFill, { width: `${progress * 100}%` }]} />
              </View>
            </View>
          </Card>
        </View>

        {/* Next Recipient Card */}
        {next_recipient && (
          <Card>
            <Text style={styles.sectionTitle}>Next Payout</Text>
            <Divider style={styles.divider} />
            <View style={styles.recipientRow}>
              <View style={styles.avatar}>
                <Text style={styles.avatarText}>
                  {next_recipient.name.charAt(0).toUpperCase()}
                </Text>
              </View>
              <View style={styles.recipientInfo}>
                <Text style={styles.recipientName}>{next_recipient.name}</Text>
                <Text style={styles.recipientPosition}>
                  Position {next_recipient.rotation_position}
                </Text>
              </View>
            </View>
            <Text style={styles.payoutAmount}>
              Amount: GHS {totalExpected.toFixed(2)}
            </Text>
            {progress >= 1 && (
              <Button
                onPress={handleApprovePayout}
                loading={approving}
                mode="contained"
                style={styles.approveButton}
              >
                Approve Payout
              </Button>
            )}
          </Card>
        )}

        {/* Members List */}
        <Card style={styles.membersCard}>
          <View style={styles.membersHeader}>
            <Text style={styles.membersHeaderIcon}>👥</Text>
            <Text style={styles.membersHeaderTitle}>Group Members</Text>
          </View>
          <Divider style={styles.divider} />
          <View style={styles.membersList}>
            {members.map((member, index) => {
              const isCurrentUserMember = currentUser?.id === member.user_id;
              const isAdminUser = members.some(m => m.is_admin && m.user_id === currentUser?.id);

              return (
                <View 
                  key={member.user_id} 
                  style={[
                    styles.memberCard,
                    isCurrentUserMember && styles.currentUserCard
                  ]}
                >
                  <View style={styles.memberLeft}>
                    <View style={[
                      styles.positionBadge,
                      isCurrentUserMember && styles.currentUserPositionBadge
                    ]}>
                      <Text style={[
                        styles.positionText,
                        isCurrentUserMember && styles.currentUserPositionText
                      ]}>
                        {member.rotation_position}
                      </Text>
                    </View>
                    
                    <View style={styles.memberInfo}>
                      <View style={styles.memberNameRow}>
                        <Text style={styles.memberName}>
                          {member.display_name}
                        </Text>
                        {member.alias && (
                          <Text style={styles.aliasText}>
                            ({member.alias})
                          </Text>
                        )}
                        {member.is_admin && <Text style={styles.adminCrown}>👑</Text>}
                        {isCurrentUserMember && (
                          <View style={styles.youBadge}>
                            <Text style={styles.youBadgeText}>You</Text>
                          </View>
                        )}
                      </View>
                      <Text style={styles.memberPhone}>{member.phone_number}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.memberRight}>
                    <View style={[
                      styles.statusBadge,
                      member.paid_current_round ? styles.paidStatusBadge : styles.unpaidStatusBadge
                    ]}>
                      <Text style={[
                        styles.statusBadgeText,
                        member.paid_current_round ? styles.paidStatusText : styles.unpaidStatusText
                      ]}>
                        {member.paid_current_round ? 'PAID' : 'UNPAID'}
                      </Text>
                    </View>

                    {/* Show payment button for unpaid members */}
                    {!member.paid_current_round && (isCurrentUserMember || isAdminUser) && (
                      <TouchableOpacity
                        onPress={() => {
                          if (isCurrentUserMember) {
                            // User pays their own payment
                            Alert.alert(
                              'Payment Request',
                              'Request payment for your contribution?',
                              [
                                { text: 'Cancel', style: 'cancel' },
                                {
                                  text: 'Pay Now',
                                  onPress: async () => {
                                    try {
                                      // First, trigger a payment to create the payment record
                                      await paymentService.triggerPayment({
                                        group_id: group.id
                                      });
                                      Alert.alert('Success', 'Payment request sent! Check your phone for MoMo prompt.');
                                      fetchDashboard();
                                    } catch (error: any) {
                                      Alert.alert('Error', error.message || 'Failed to send payment request');
                                    }
                                  },
                                },
                              ]
                            );
                          } else if (isAdminUser) {
                            // Admin requests payment from member
                            Alert.alert(
                              'Request Payment',
                              `Request payment from ${member.name}?`,
                              [
                                { text: 'Cancel', style: 'cancel' },
                                {
                                  text: 'Send Request',
                                  onPress: async () => {
                                    try {
                                      await paymentService.adminRequestPayment({
                                        group_id: group.id,
                                        user_id: member.user_id,
                                        round_number: group.current_round,
                                      });
                                      Alert.alert('Success', `${member.name} will receive a payment request on their phone.`);
                                      fetchDashboard();
                                    } catch (error: any) {
                                      Alert.alert('Error', error.message || 'Failed to send payment request');
                                    }
                                  },
                                },
                              ]
                            );
                          }
                        }}
                        style={[
                          styles.payButton,
                          isCurrentUserMember ? styles.userPayButton : styles.adminPayButton
                        ]}
                      >
                        <Text style={styles.payButtonIcon}>$</Text>
                        <Text style={styles.payButtonText}>
                          {isCurrentUserMember ? 'Pay Now' : 'Request Payment'}
                        </Text>
                      </TouchableOpacity>
                    )}
                  </View>
                </View>
              );
            })}
          </View>
        </Card>
      </ScrollView>

      {/* Invite Member Modal */}
      <Modal
        visible={inviteModalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setInviteModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Invite Member</Text>
            <Text style={styles.modalSubtitle}>
              Enter the phone number of the person you want to invite
            </Text>
            
            <TextInput
              style={styles.input}
              placeholder="+233201234567"
              value={phoneNumber}
              onChangeText={setPhoneNumber}
              keyboardType="phone-pad"
              autoCapitalize="none"
              autoFocus={true}
            />
            
            <Text style={styles.helperText}>
              ℹ️ They will receive an SMS with the group code
            </Text>

            <View style={styles.modalButtons}>
              <Button
                onPress={() => {
                  setPhoneNumber('');
                  setInviteModalVisible(false);
                }}
                mode="outlined"
                style={styles.modalButton}
              >
                Cancel
              </Button>
              <Button
                onPress={handleInviteMember}
                mode="contained"
                loading={inviting}
                style={styles.modalButton}
              >
                Send Invitation
              </Button>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  scrollContent: {
    padding: spacing.md,
  },
  groupInfoCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  groupCodeContainer: {
    flex: 1,
  },
  groupCodeLabel: {
    fontSize: 12,
    color: '#666666',
    fontWeight: '500',
    marginBottom: 4,
  },
  groupCode: {
    fontSize: 18,
    color: '#4CAF50',
    fontWeight: '700',
  },
  roundInfoContainer: {
    marginTop: spacing.md,
    marginBottom: spacing.md,
  },
  contributionAmount: {
    fontSize: 14,
    color: '#666666',
    marginTop: 4,
    fontWeight: '500',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  groupCode: {
    ...typography.body,
    color: colors.primary,
    fontWeight: '600',
  },
  roundInfo: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  statsRow: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.md,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  statContent: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#666666',
    fontWeight: '500',
    marginBottom: spacing.xs,
  },
  statValue: {
    fontSize: 20,
    color: '#4CAF50',
    fontWeight: '700',
    marginBottom: spacing.xs,
  },
  statSubtext: {
    fontSize: 11,
    color: '#999999',
    marginBottom: spacing.sm,
  },
  progressBar: {
    width: '100%',
    height: 4,
    backgroundColor: '#E0E0E0',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    borderRadius: 2,
  },
  sectionTitle: {
    ...typography.h3,
    color: '#333333',
    marginBottom: spacing.lg,
    fontWeight: '700',
    fontSize: 18,
  },
  membersCard: {
    marginTop: spacing.lg,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
  },
  membersHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  membersHeaderIcon: {
    fontSize: 24,
    marginRight: spacing.sm,
    color: '#059669',
  },
  membersHeaderTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#1E293B',
    letterSpacing: -0.5,
  },
  membersList: {
    gap: spacing.sm,
  },
  divider: {
    marginBottom: spacing.md,
  },
  recipientRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  avatarText: {
    fontSize: 20,
    color: colors.surface,
    fontWeight: 'bold',
  },
  recipientInfo: {
    flex: 1,
  },
  recipientName: {
    ...typography.body,
    color: colors.text,
    fontWeight: '600',
  },
  recipientPosition: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  payoutAmount: {
    ...typography.body,
    color: colors.primary,
    fontWeight: '600',
    marginBottom: spacing.md,
  },
  approveButton: {
    marginTop: spacing.sm,
  },
  memberCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.md,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: spacing.sm,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  currentUserCard: {
    borderWidth: 2,
    borderColor: '#059669',
    backgroundColor: '#F0FDF4',
    shadowColor: '#059669',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  memberLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  positionBadge: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#E5E7EB',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  currentUserPositionBadge: {
    backgroundColor: '#059669',
  },
  positionText: {
    fontWeight: 'bold',
    fontSize: 16,
    color: '#374151',
  },
  currentUserPositionText: {
    color: '#FFFFFF',
  },
  memberInfo: {
    flex: 1,
  },
  memberNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  memberName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1E293B',
  },
  aliasText: {
    fontSize: 14,
    fontWeight: '400',
    color: '#64748B',
    marginLeft: spacing.xs,
    fontStyle: 'italic',
  },
  adminCrown: {
    fontSize: 20,
    marginLeft: spacing.xs,
  },
  youBadge: {
    backgroundColor: '#A7F3D0',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    marginLeft: spacing.sm,
  },
  youBadgeText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#059669',
  },
  memberPhone: {
    fontSize: 14,
    color: '#64748B',
    fontFamily: 'monospace',
  },
  memberRight: {
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: spacing.sm,
    minWidth: 120,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginBottom: spacing.sm,
  },
  paidStatusBadge: {
    backgroundColor: '#D1FAE5',
  },
  unpaidStatusBadge: {
    backgroundColor: '#FEE2E2',
  },
  statusBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  paidStatusText: {
    color: '#047857',
  },
  unpaidStatusText: {
    color: '#DC2626',
  },
  payButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  userPayButton: {
    backgroundColor: '#059669',
    shadowColor: '#059669',
    shadowOpacity: 0.3,
  },
  adminPayButton: {
    backgroundColor: '#3B82F6',
    shadowColor: '#3B82F6',
    shadowOpacity: 0.3,
  },
  payButtonIcon: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginRight: 4,
  },
  payButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  inviteButton: {
    marginTop: spacing.md,
    borderRadius: 12,
    height: 48,
  },
  settingsButton: {
    marginTop: spacing.sm,
    borderRadius: 12,
    height: 48,
  },
  invitationRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  invitationPhone: {
    ...typography.body,
    color: colors.text,
    fontWeight: '500',
  },
  invitationDate: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  invitationCount: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    width: '85%',
    maxWidth: 400,
  },
  modalTitle: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  modalSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  input: {
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: spacing.md,
    fontSize: 16,
    marginBottom: spacing.sm,
  },
  helperText: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  modalButton: {
    flex: 1,
  },
});

