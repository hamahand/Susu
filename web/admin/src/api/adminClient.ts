import type {
  DashboardStats,
  ActivityItem,
  UserListItem,
  UserDetail,
  GroupListItem,
  GroupDetail,
  PaymentListItem,
  PayoutListItem,
  InvitationItem,
  SettingItem,
  AuditLogItem,
  AdminUser,
  RevenueAnalytics,
  UserAnalytics,
  GroupAnalytics
} from '../types/admin';

const API_BASE = 'http://localhost:8000';

class AdminAPIClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('admin_token', token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('admin_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('admin_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        this.clearToken();
        window.location.href = '/';
      }
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Authentication
  async login(phone_number: string, password: string) {
    const response = await this.request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ phone_number, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  async getCurrentUser() {
    return this.request<UserDetail>('/auth/me');
  }

  // Dashboard & Analytics
  async getDashboardStats() {
    return this.request<DashboardStats>('/admin/dashboard/stats');
  }

  async getDashboardActivity(limit: number = 20) {
    return this.request<ActivityItem[]>(`/admin/dashboard/activity?limit=${limit}`);
  }

  async getRevenueAnalytics(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params}` : '';
    return this.request<RevenueAnalytics>(`/admin/analytics/revenue${query}`);
  }

  async getUserAnalytics() {
    return this.request<UserAnalytics>('/admin/analytics/users');
  }

  async getGroupAnalytics() {
    return this.request<GroupAnalytics>('/admin/analytics/groups');
  }

  async getAnalyticsOverview(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params}` : '';
    return this.request(`/admin/analytics/overview${query}`);
  }

  async getFinancialAnalytics(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params}` : '';
    return this.request(`/admin/analytics/financial${query}`);
  }

  async getPaymentTrends(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params}` : '';
    return this.request(`/admin/analytics/payment-trends${query}`);
  }

  // Bulk Operations
  async bulkDeactivateUsers(userIds: number[]) {
    return this.request('/admin/bulk/users/deactivate', {
      method: 'POST',
      body: JSON.stringify(userIds),
    });
  }

  async bulkVerifyKYC(userIds: number[]) {
    return this.request('/admin/bulk/users/verify-kyc', {
      method: 'POST',
      body: JSON.stringify(userIds),
    });
  }

  async bulkRetryPayments(paymentIds: number[]) {
    return this.request('/admin/bulk/payments/retry', {
      method: 'POST',
      body: JSON.stringify(paymentIds),
    });
  }

  async bulkSuspendGroups(groupIds: number[]) {
    return this.request('/admin/bulk/groups/suspend', {
      method: 'POST',
      body: JSON.stringify(groupIds),
    });
  }

  // Database Management
  async getDatabaseTables() {
    return this.request('/admin/database/tables');
  }

  async executeDatabaseQuery(query: string) {
    return this.request(`/admin/database/query?query=${encodeURIComponent(query)}`, {
      method: 'POST',
    });
  }

  async getDatabaseStats() {
    return this.request('/admin/database/stats');
  }

  async getDatabaseMigrations() {
    return this.request('/admin/database/migrations');
  }

  // System Configuration
  async getSystemHealth() {
    return this.request('/admin/system/health');
  }

  async getServicesStatus() {
    return this.request('/admin/system/services');
  }

  // User Management
  async getUsers(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    user_type?: string;
    kyc_verified?: boolean;
    is_admin?: boolean;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString() ? `?${queryParams}` : '';
    return this.request<UserListItem[]>(`/admin/users${query}`);
  }

  async getUserDetail(userId: number) {
    return this.request<UserDetail>(`/admin/users/${userId}`);
  }

  async updateUser(
    userId: number,
    data: { name?: string; email?: string; kyc_verified?: boolean }
  ) {
    return this.request(`/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deactivateUser(userId: number) {
    return this.request(`/admin/users/${userId}`, { method: 'DELETE' });
  }

  async verifyUserKYC(userId: number) {
    return this.request(`/admin/users/${userId}/verify-kyc`, { method: 'POST' });
  }

  async resetUserPassword(userId: number, newPassword: string) {
    return this.request(`/admin/users/${userId}/reset-password?new_password=${newPassword}`, {
      method: 'POST',
    });
  }

  async getUserActivity(userId: number) {
    return this.request(`/admin/users/${userId}/activity`);
  }

  // Group Management
  async getGroups(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    status?: string;
    cash_only?: boolean;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString() ? `?${queryParams}` : '';
    return this.request<GroupListItem[]>(`/admin/groups${query}`);
  }

  async getGroupDetail(groupId: number) {
    return this.request<GroupDetail>(`/admin/groups/${groupId}`);
  }

  async updateGroup(
    groupId: number,
    data: { name?: string; contribution_amount?: number; status?: string }
  ) {
    return this.request(`/admin/groups/${groupId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async suspendGroup(groupId: number) {
    return this.request(`/admin/groups/${groupId}/suspend`, { method: 'POST' });
  }

  async reactivateGroup(groupId: number) {
    return this.request(`/admin/groups/${groupId}/reactivate`, { method: 'POST' });
  }

  async deleteGroup(groupId: number) {
    return this.request(`/admin/groups/${groupId}`, { method: 'DELETE' });
  }

  async removeGroupMember(groupId: number, userId: number) {
    return this.request(`/admin/groups/${groupId}/remove-member?user_id=${userId}`, {
      method: 'POST',
    });
  }

  // Payment Management
  async getPayments(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    payment_type?: string;
    start_date?: string;
    end_date?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString() ? `?${queryParams}` : '';
    return this.request<PaymentListItem[]>(`/admin/payments${query}`);
  }

  async getPaymentDetail(paymentId: number) {
    return this.request(`/admin/payments/${paymentId}`);
  }

  async updatePayment(paymentId: number, data: { status?: string }) {
    return this.request(`/admin/payments/${paymentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getPendingPayments() {
    return this.request('/admin/payments/pending');
  }

  async getFailedPayments() {
    return this.request('/admin/payments/failed');
  }

  // Payout Management
  async getPayouts(params?: { skip?: number; limit?: number; status?: string }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString() ? `?${queryParams}` : '';
    return this.request<PayoutListItem[]>(`/admin/payouts${query}`);
  }

  async getPayoutDetail(payoutId: number) {
    return this.request(`/admin/payouts/${payoutId}`);
  }

  async approvePayout(payoutId: number) {
    return this.request(`/admin/payouts/${payoutId}/approve`, { method: 'POST' });
  }

  async rejectPayout(payoutId: number, reason: string) {
    return this.request(`/admin/payouts/${payoutId}/reject?reason=${reason}`, {
      method: 'POST',
    });
  }

  // Invitation Management
  async getInvitations(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString() ? `?${queryParams}` : '';
    return this.request<InvitationItem[]>(`/admin/invitations${query}`);
  }

  async expireInvitation(invitationId: number) {
    return this.request(`/admin/invitations/${invitationId}/expire`, { method: 'POST' });
  }

  async deleteInvitation(invitationId: number) {
    return this.request(`/admin/invitations/${invitationId}`, { method: 'DELETE' });
  }

  // System Settings
  async getSettings(category?: string) {
    const query = category ? `?category=${category}` : '';
    return this.request<SettingItem[]>(`/admin/settings${query}`);
  }

  async getSettingsByCategory(category: string) {
    return this.request<SettingItem[]>(`/admin/settings/${category}`);
  }

  async updateSetting(settingKey: string, value: string) {
    return this.request(`/admin/settings/${settingKey}`, {
      method: 'PUT',
      body: JSON.stringify({ setting_value: value }),
    });
  }

  async createSetting(data: {
    setting_key: string;
    setting_value: string;
    category: string;
    description?: string;
  }) {
    return this.request('/admin/settings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Audit Logs
  async getAuditLogs(params?: {
    skip?: number;
    limit?: number;
    entity_type?: string;
    action?: string;
    performed_by?: number;
    start_date?: string;
    end_date?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString() ? `?${queryParams}` : '';
    return this.request<AuditLogItem[]>(`/admin/audit-logs${query}`);
  }

  async getEntityAuditLogs(entityType: string, entityId: number) {
    return this.request<AuditLogItem[]>(
      `/admin/audit-logs/entity/${entityType}/${entityId}`
    );
  }

  // Admin Management
  async getAdmins() {
    return this.request<AdminUser[]>('/admin/admins');
  }

  async createAdmin(data: {
    phone_number: string;
    name: string;
    password: string;
    admin_role: string;
  }) {
    return this.request('/admin/admins', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAdminRole(adminId: number, newRole: string) {
    return this.request(`/admin/admins/${adminId}?new_role=${newRole}`, {
      method: 'PUT',
    });
  }

  async revokeAdminAccess(adminId: number) {
    return this.request(`/admin/admins/${adminId}`, { method: 'DELETE' });
  }

  // Export Functions
  async exportUsers() {
    const token = this.getToken();
    window.open(`${API_BASE}/admin/export/users?token=${token}`, '_blank');
  }

  async exportPayments(startDate?: string, endDate?: string) {
    const token = this.getToken();
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `&${params}` : '';
    window.open(`${API_BASE}/admin/export/payments?token=${token}${query}`, '_blank');
  }
}

export const adminAPI = new AdminAPIClient();

