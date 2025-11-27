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
  creator_id: number;
  created_at: string;
  member_count?: number;
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

// Alias for backward compatibility
export type GroupMember = MemberInfo;

// Payment types
export enum PaymentStatus {
  PENDING = 'pending',
  SUCCESS = 'success',
  FAILED = 'failed',
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
  retry_count: number;
  created_at: string;
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

// Invitation types
export interface Invitation {
  id: number;
  group_id: number;
  phone_number: string;
  created_at: string;
  expires_at: string;
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
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CreateGroupRequest {
  name: string;
  contribution_amount: number;
  num_cycles: number;
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

export interface OTPResponse {
  sent_to: string;
  ttl_minutes: number;
}

export interface UpdateProfileRequest {
  username?: string;
  email?: string;
}

