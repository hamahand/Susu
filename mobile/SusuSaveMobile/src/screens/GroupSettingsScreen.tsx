import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, Switch, Appbar } from 'react-native-paper';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { colors, spacing, typography } from '../theme';
import { groupService } from '../api/groupService';
import { Group, GroupPrivacySettings } from '../types/api';

export const GroupSettingsScreen: React.FC<any> = ({ route, navigation }) => {
  const { groupId } = route.params;
  const [group, setGroup] = useState<Group | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<GroupPrivacySettings>({
    show_alias_to_members: true,
    show_real_name_to_members: false,
    show_phone_to_members: false,
  });

  useEffect(() => {
    loadGroupDetails();
  }, [groupId]);

  const loadGroupDetails = async () => {
    try {
      const groupData = await groupService.getGroupDetails(groupId);
      setGroup(groupData);
      
      // Initialize settings from group data or use defaults
      setSettings({
        show_alias_to_members: groupData.show_alias_to_members ?? true,
        show_real_name_to_members: groupData.show_real_name_to_members ?? false,
        show_phone_to_members: groupData.show_phone_to_members ?? false,
      });
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to load group details');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const updatedGroup = await groupService.updateGroupPrivacy(groupId, settings);
      setGroup(updatedGroup);
      Alert.alert('Success', 'Privacy settings updated successfully');
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to update privacy settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (!group) {
    return (
      <View style={styles.container}>
        <Text>Group not found</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Group Settings" />
      </Appbar.Header>

      <ScrollView style={styles.scrollView}>
        <Card style={styles.headerCard}>
          <Text style={styles.groupName}>{group.name}</Text>
          <Text style={styles.groupCode}>Code: {group.group_code}</Text>
        </Card>

        <Card style={styles.settingsCard}>
          <Text style={styles.cardTitle}>Privacy Settings</Text>
          <Text style={styles.cardDescription}>
            Control what member information is visible to non-admin members. Admins always see full information.
          </Text>

          {/* Show Alias Toggle */}
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Show Aliases to Members</Text>
              <Text style={styles.settingDescription}>
                Allow non-admin members to see other members' generated aliases
              </Text>
            </View>
            <Switch
              value={settings.show_alias_to_members}
              onValueChange={(value) =>
                setSettings({ ...settings, show_alias_to_members: value })
              }
              color={colors.primary}
            />
          </View>

          {/* Show Real Names Toggle */}
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Show Real Names to Members</Text>
              <Text style={styles.settingDescription}>
                Allow non-admin members to see other members' real names (overrides alias settings)
              </Text>
            </View>
            <Switch
              value={settings.show_real_name_to_members}
              onValueChange={(value) =>
                setSettings({ ...settings, show_real_name_to_members: value })
              }
              color={colors.primary}
            />
          </View>

          {/* Show Phone Numbers Toggle */}
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Show Phone Numbers to Members</Text>
              <Text style={styles.settingDescription}>
                Allow non-admin members to see other members' phone numbers (will show masked numbers if disabled)
              </Text>
            </View>
            <Switch
              value={settings.show_phone_to_members}
              onValueChange={(value) =>
                setSettings({ ...settings, show_phone_to_members: value })
              }
              color={colors.primary}
            />
          </View>
        </Card>

        <Button 
          onPress={handleSave} 
          loading={saving} 
          mode="contained" 
          style={styles.saveButton}
        >
          Save Settings
        </Button>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>ℹ️ Important Notes</Text>
          <Text style={styles.infoText}>
            • Admins always see full member information regardless of these settings
          </Text>
          <Text style={styles.infoText}>
            • Each member always sees their own information
          </Text>
          <Text style={styles.infoText}>
            • Phone numbers are masked as "*******5678" when hidden
          </Text>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollView: {
    flex: 1,
  },
  headerCard: {
    margin: spacing.md,
    padding: spacing.md,
    alignItems: 'center',
  },
  groupName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  groupCode: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  settingsCard: {
    margin: spacing.md,
    padding: spacing.md,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  cardDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
    lineHeight: 20,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.lg,
    paddingBottom: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  settingInfo: {
    flex: 1,
    marginRight: spacing.md,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  settingDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  saveButton: {
    margin: spacing.md,
    marginTop: spacing.sm,
  },
  infoCard: {
    margin: spacing.md,
    marginTop: 0,
    padding: spacing.md,
    backgroundColor: colors.primaryLight + '20',
    borderRadius: 8,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  infoText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    lineHeight: 20,
  },
});

