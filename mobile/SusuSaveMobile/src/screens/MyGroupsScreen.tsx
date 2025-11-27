import React, { useState, useEffect, useCallback } from 'react';
import { View, StyleSheet, FlatList, RefreshControl, Alert } from 'react-native';
import { Text, FAB, Appbar } from 'react-native-paper';
import { useAuth } from '../store/authContext';
import { groupService } from '../api/groupService';
import { Group } from '../types/api';
import { GroupCard } from '../components/GroupCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { NotificationBell } from '../components/NotificationBell';
import { Button } from '../components/Button';
import { colors, spacing, typography } from '../theme';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { HomeStackParamList } from '../navigation/types';
import { useFocusEffect } from '@react-navigation/native';

type MyGroupsScreenProps = {
  navigation: NativeStackNavigationProp<HomeStackParamList, 'MyGroups'>;
};

export const MyGroupsScreen: React.FC<MyGroupsScreenProps> = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchGroups = async () => {
    try {
      const data = await groupService.getMyGroups();
      setGroups(data);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to load groups');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Refresh groups when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      fetchGroups();
    }, [])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchGroups();
  }, []);

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

  const renderEmpty = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyIcon}>📊</Text>
      <Text style={styles.emptyTitle}>No Groups Yet</Text>
      <Text style={styles.emptyText}>
        Create a savings group or join one with a group code
      </Text>
      <View style={styles.emptyButtons}>
        <Button onPress={() => navigation.navigate('CreateGroup')} mode="contained">
          Create Group
        </Button>
        <Button onPress={() => navigation.navigate('JoinGroup')} mode="outlined">
          Join Group
        </Button>
      </View>
    </View>
  );

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title={`Hello, ${user?.name || 'User'}`} />
        <NotificationBell onPress={() => navigation.navigate('Notifications')} />
        <Appbar.Action icon="account-plus" onPress={() => navigation.navigate('JoinGroup')} />
        <Appbar.Action icon="logout" onPress={handleLogout} />
      </Appbar.Header>

      <FlatList
        data={groups}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <GroupCard
            group={item}
            onPress={() => navigation.navigate('GroupDashboard', { groupId: item.id })}
          />
        )}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      />

      <FAB
        style={styles.fab}
        icon="plus"
        label="Create Group"
        onPress={() => navigation.navigate('CreateGroup')}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  listContent: {
    padding: spacing.md,
    flexGrow: 1,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: spacing.lg,
  },
  emptyTitle: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
  emptyButtons: {
    gap: spacing.md,
    width: '100%',
    paddingHorizontal: spacing.lg,
  },
  fab: {
    position: 'absolute',
    margin: spacing.md,
    right: 0,
    bottom: 0,
    backgroundColor: colors.primary,
  },
});

