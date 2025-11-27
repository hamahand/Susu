import React from 'react';
import { StyleSheet, View } from 'react-native';
import { Text, ProgressBar } from 'react-native-paper';
import { Card } from './Card';
import { Group } from '../types/api';
import { colors, spacing, typography, borderRadius } from '../theme';

interface GroupCardProps {
  group: Group;
  onPress: () => void;
}

export const GroupCard: React.FC<GroupCardProps> = ({ group, onPress }) => {
  const progress = group.current_round / group.num_cycles;

  return (
    <Card onPress={onPress}>
      <View style={styles.header}>
        <Text style={styles.groupName}>{group.name}</Text>
        <View style={[styles.statusBadge, { backgroundColor: colors.success }]}>
          <Text style={styles.statusText}>{group.status}</Text>
        </View>
      </View>

      <Text style={styles.groupCode}>Code: {group.group_code}</Text>

      <View style={styles.stats}>
        <Text style={styles.statText}>
          Round {group.current_round} of {group.num_cycles}
        </Text>
        <Text style={styles.amount}>GHS {group.contribution_amount}</Text>
      </View>

      {group.member_count !== undefined && (
        <Text style={styles.memberCount}>
          {group.member_count} member{group.member_count !== 1 ? 's' : ''}
        </Text>
      )}

      <ProgressBar
        progress={progress}
        color={colors.primary}
        style={styles.progressBar}
      />
    </Card>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  groupName: {
    ...typography.h3,
    color: colors.text,
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.sm,
  },
  statusText: {
    fontSize: 12,
    color: colors.surface,
    textTransform: 'capitalize',
    fontWeight: '600',
  },
  groupCode: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  statText: {
    ...typography.body,
    color: colors.text,
  },
  amount: {
    ...typography.body,
    color: colors.primary,
    fontWeight: '600',
  },
  memberCount: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  progressBar: {
    height: 8,
    borderRadius: borderRadius.sm,
  },
});

