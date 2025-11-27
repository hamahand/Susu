// Admin Types

export interface DashboardStats {
  total_users: number;
  active_users: number;
  total_groups: number;
  active_groups: number;
  total_revenue: number;
  pending_payments: number;
  pending_payouts: number;
  failed_payments: number;
  pending_invitations: number;
  kyc_verified: number;
  kyc_pending: number;
  new_users_30d: number;
}

export interface ActivityItem {
  type: string;
  timestamp: string;
  description: string;
  user_id?: number;
  group_id?: number;
  payment_id?: number;
}

export interface UserListItem {
  id: number;
  name: string;
  phone_number: string;
  email?: string;
  user_type: string;
  kyc_verified: boolean;
  is_system_admin: boolean;
  admin_role?: string;
  created_at: string;
}

export interface UserDetail {
  id: number;
  name: string;
  phone_number: string;
  email?: string;
  user_type: string;
  kyc_verified: boolean;
  kyc_verified_at?: string;
  is_system_admin: boolean;
  admin_role?: string;
  last_login?: string;
  created_at: string;
  total_groups: number;
  total_payments: number;
  active_memberships: number;
}

export interface GroupListItem {
  id: number;
  group_code: string;
  name: string;
  contribution_amount: number;
  num_cycles: number;
  current_round: number;
  status: string;
  cash_only: boolean;
  member_count: number;
  total_contributions: number;
  created_at: string;
}

export interface GroupDetail {
  id: number;
  group_code: string;
  name: string;
  contribution_amount: number;
  num_cycles: number;
  current_round: number;
  status: string;
  cash_only: boolean;
  creator_id: number;
  created_at: string;
  members: Array<{
    user_id: number;
    name: string;
    phone: string;
    rotation_position: number;
    is_admin: boolean;
  }>;
  payments_summary: {
    total_paid: number;
    pending_payments: number;
  };
}

export interface PaymentListItem {
  id: number;
  transaction_id?: string;
  user_id: number;
  user_name: string;
  group_id: number;
  group_name: string;
  amount: number;
  status: string;
  payment_type: string;
  round_number: number;
  payment_date?: string;
  created_at: string;
}

export interface PayoutListItem {
  id: number;
  recipient_id: number;
  recipient_name: string;
  group_id: number;
  group_name: string;
  amount: number;
  status: string;
  payout_date?: string;
  created_at: string;
}

export interface InvitationItem {
  id: number;
  group_id: number;
  group_name: string;
  phone_number: string;
  invited_by: string;
  status: string;
  created_at: string;
  accepted_at?: string;
}

export interface SettingItem {
  id: number;
  setting_key: string;
  setting_value: string;
  category: string;
  description?: string;
  updated_at?: string;
}

export interface AuditLogItem {
  id: number;
  entity_type: string;
  entity_id?: number;
  action: string;
  performed_by?: number;
  timestamp: string;
  details?: string;
}

export interface AdminUser {
  id: number;
  name: string;
  phone: string;
  admin_role?: string;
  last_login?: string;
  created_at: string;
}

export interface RevenueAnalytics {
  period: {
    start: string;
    end: string;
  };
  total_revenue: number;
  payment_count: number;
  average_payment: number;
  revenue_by_type: {
    momo: number;
    cash: number;
  };
}

export interface UserAnalytics {
  total_users: number;
  user_types: {
    app: number;
    ussd: number;
  };
  growth: Array<{
    period: string;
    new_users: number;
  }>;
  active_users_30d: number;
  activity_rate: number;
}

export interface GroupAnalytics {
  total_groups: number;
  by_status: {
    active: number;
    completed: number;
    suspended: number;
  };
  average_group_size: number;
  payment_types: {
    cash_only: number;
    momo_enabled: number;
  };
}

