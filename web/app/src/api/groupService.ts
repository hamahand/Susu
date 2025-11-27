import apiClient from './client';
import {
  Group,
  GroupDashboard,
  CreateGroupRequest,
  JoinGroupRequest,
  Invitation,
} from '../types/api';

export const groupService = {
  /**
   * Create a new group
   */
  async createGroup(data: CreateGroupRequest): Promise<Group> {
    const response = await apiClient.post<Group>('/groups', data);
    return response.data;
  },

  /**
   * Get all groups the user is part of
   */
  async getMyGroups(): Promise<Group[]> {
    const response = await apiClient.get<Group[]>('/groups/my-groups');
    return response.data;
  },

  /**
   * Get group details by ID
   */
  async getGroupDetails(groupId: number): Promise<Group> {
    const response = await apiClient.get<Group>(`/groups/${groupId}`);
    return response.data;
  },

  /**
   * Get group dashboard with detailed stats
   */
  async getGroupDashboard(groupId: number): Promise<GroupDashboard> {
    const response = await apiClient.get<GroupDashboard>(`/groups/${groupId}/dashboard`);
    return response.data;
  },

  /**
   * Join a group using group code
   */
  async joinGroup(data: JoinGroupRequest): Promise<{ message: string; group_id: number; rotation_position: number }> {
    const response = await apiClient.post('/groups/join', data);
    return response.data;
  },

  /**
   * Invite a member to a group by phone number
   */
  async inviteMember(groupId: number, phoneNumber: string): Promise<Invitation> {
    const response = await apiClient.post(`/groups/${groupId}/invite`, {
      phone_number: phoneNumber,
    });
    return response.data;
  },

  /**
   * Get pending invitations for a group
   */
  async getPendingInvitations(groupId: number): Promise<Invitation[]> {
    const response = await apiClient.get(`/groups/${groupId}/invitations`);
    return response.data;
  },
};

