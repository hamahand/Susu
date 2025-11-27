import React from 'react';
import './StatusBadge.css';

type Status = 'active' | 'completed' | 'suspended' | 'pending' | 'success' | 'failed' | 'paid' | 'unpaid' | 'approved';

interface StatusBadgeProps {
  status: Status;
  size?: 'small' | 'medium';
}

const statusConfig: Record<Status, { label: string; color: string }> = {
  active: { label: 'Active', color: 'success' },
  completed: { label: 'Completed', color: 'info' },
  suspended: { label: 'Suspended', color: 'warning' },
  pending: { label: 'Pending', color: 'warning' },
  success: { label: 'Success', color: 'success' },
  failed: { label: 'Failed', color: 'error' },
  paid: { label: 'Paid', color: 'success' },
  unpaid: { label: 'Unpaid', color: 'warning' },
  approved: { label: 'Approved', color: 'success' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'medium' }) => {
  const config = statusConfig[status];
  const classes = ['status-badge', `status-badge-${config.color}`, `status-badge-${size}`].join(' ');

  return <span className={classes}>{config.label}</span>;
};

