// User types
export enum UserType {
  APP = 'app',
  USSD = 'ussd',
}

export interface User {
  id: number;
  phone_number: string;
  name: string;
  email?: string | null;
  user_type: UserType;
  created_at: string;
}

// Group types
export enum GroupStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  SUSPENDED = 'suspended',
}

export interface Group {
  id: number;
  group_code: string;
  name: string;
  contribution_amount: number;
  num_cycles: number;
  current_round: number;
  status: GroupStatus;
  cash_only: boolean;
  creator_id: number;
  created_at: string;
  member_count?: number;
  show_alias_to_members?: boolean;
  show_real_name_to_members?: boolean;
  show_phone_to_members?: boolean;
}

// Membership types
export interface Membership {
  id: number;
  user_id: number;
  group_id: number;
  rotation_position: number;
  is_admin: boolean;
  is_active: boolean;
  join_date: string;
}

export interface MemberInfo {
  user_id: number;
  name: string;
  display_name: string;  // Real name for admins/self, alias for others
  alias?: string;  // Only shown to admins
  phone_number: string;
  rotation_position: number;
  is_admin: boolean;
  paid_current_round: boolean;
}

// Payment types
export enum PaymentStatus {
  PENDING = 'pending',
  SUCCESS = 'success',
  FAILED = 'failed',
}

export enum PaymentType {
  MOMO = 'momo',
  CASH = 'cash',
}

export interface Payment {
  id: number;
  transaction_id: string | null;
  user_id: number;
  group_id: number;
  round_number: number;
  amount: number;
  payment_date: string | null;
  status: PaymentStatus;
  payment_type: PaymentType;
  marked_paid_by: number | null;
  retry_count: number;
  created_at: string;
}

export interface UnpaidPayment {
  payment_id: number | null;
  group_id: number;
  group_name: string;
  round_number: number;
  amount: number;
  is_paid: boolean;
  is_cash_only: boolean;
}

// Payout types
export enum PayoutStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  PAID = 'paid',
  FAILED = 'failed',
}

export interface Payout {
  id: number;
  group_id: number;
  round_number: number;
  recipient_id: number;
  payout_date: string | null;
  amount: number;
  status: PayoutStatus;
  transaction_id: string | null;
  created_at: string;
}

// Dashboard types
export interface GroupDashboard {
  group: Group;
  members: MemberInfo[];
  total_collected_current_round: number;
  next_recipient: MemberInfo | null;
  next_payout_date: string | null;
}

// Request/Response types
export interface LoginRequest {
  phone_number: string;
  password: string;
}

export interface RegisterRequest {
  phone_number: string;
  name: string;
  password: string;
  user_type: UserType;
  payment_method?: 'auto' | 'manual' | 'ussd';
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CreateGroupRequest {
  name: string;
  contribution_amount: number;
  num_cycles: number;
  cash_only?: boolean;
}

export interface JoinGroupRequest {
  group_code: string;
}

export interface TriggerPaymentRequest {
  group_id: number;
}

export interface ApiError {
  detail: string;
}

export interface GroupPrivacySettings {
  show_alias_to_members: boolean;
  show_real_name_to_members: boolean;
  show_phone_to_members: boolean;
}

// Notification types
export interface Notification {
  id: number;
  user_id: number;
  group_id: number;
  notification_type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  unread_count: number;
  total_returned: number;
}

