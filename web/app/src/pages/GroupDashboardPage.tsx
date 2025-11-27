import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { groupService } from '../api/groupService';
import { payoutService } from '../api/payoutService';
import { GroupDashboard, Invitation } from '../types/api';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Input } from '../components/Input';
import { PaymentButton } from '../components/PaymentButton';
import GroupMembersView from '../components/GroupMembersView';
import { formatCurrency, validatePhoneNumber } from '../utils/validation';
import { useAuth } from '../contexts/AuthContext';
import './GroupDashboardPage.css';

const GroupDashboardPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [dashboard, setDashboard] = useState<GroupDashboard | null>(null);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [approving, setApproving] = useState(false);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [inviting, setInviting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboard();
    loadInvitations();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadDashboard(true);
      loadInvitations();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [id]);

  const loadDashboard = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      const data = await groupService.getGroupDashboard(Number(id));
      setDashboard(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const loadInvitations = async () => {
    try {
      const data = await groupService.getPendingInvitations(Number(id));
      setInvitations(data);
    } catch (err) {
      // Silently fail if not admin
      console.log('Could not load invitations');
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    loadDashboard(true);
    loadInvitations();
  };

  const handleCopyCode = () => {
    if (dashboard) {
      navigator.clipboard.writeText(dashboard.group.group_code);
      alert('Group code copied to clipboard!');
    }
  };

  const handleApprovePayout = async () => {
    if (!dashboard) return;

    if (!confirm(`Approve payout of ${formatCurrency(totalExpected)} to ${dashboard.next_recipient?.name}?`)) {
      return;
    }

    setApproving(true);
    try {
      const payout = await payoutService.getCurrentPayout(dashboard.group.id);
      await payoutService.approvePayout(payout.id);
      alert('Payout approved successfully!');
      loadDashboard(true);
    } catch (err: any) {
      alert(err.message || 'Failed to approve payout');
    } finally {
      setApproving(false);
    }
  };

  const handleInviteMember = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!phoneNumber.trim()) {
      alert('Please enter a phone number');
      return;
    }

    if (!validatePhoneNumber(phoneNumber)) {
      alert('Please enter a valid phone number with country code (e.g., +233244123456)');
      return;
    }

    setInviting(true);
    try {
      await groupService.inviteMember(Number(id), phoneNumber.trim());
      alert('Invitation sent! They will receive an SMS with the group code.');
      setPhoneNumber('');
      setInviteModalOpen(false);
      loadInvitations();
    } catch (err: any) {
      alert(err.message || 'Failed to send invitation');
    } finally {
      setInviting(false);
    }
  };

  if (loading) {
    return (
      <div className="page-loading">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!dashboard || error) {
    return (
      <div className="group-dashboard-error">
        <p>{error || 'Group not found'}</p>
        <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
      </div>
    );
  }

  const { group, members, total_collected_current_round, next_recipient } = dashboard;
  const totalExpected = group.contribution_amount * members.length;
  const progress = totalExpected > 0 ? (total_collected_current_round / totalExpected) * 100 : 0;
  const isAdmin = members.some(m => m.is_admin);

  return (
    <div className="group-dashboard-page">
      <div className="group-dashboard-header">
        <div>
          <Button variant="ghost" onClick={() => navigate('/dashboard')}>
            ← Back to Groups
          </Button>
          <h1 className="group-dashboard-title">{group.name}</h1>
          <p className="group-dashboard-subtitle">
            Round {group.current_round} of {group.num_cycles}
          </p>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? '⟳' : '↻'} Refresh
        </Button>
      </div>

      {/* Group Info Card */}
      <Card>
        <div className="group-info-header">
          <div>
            <div className="group-code-container">
              <span className="group-code" onClick={handleCopyCode}>
                Code: {group.group_code} 📋
              </span>
            </div>
            <StatusBadge status={group.status as any} />
          </div>
          {isAdmin && (
            <Button onClick={() => setInviteModalOpen(true)}>
              📨 Invite Member
            </Button>
          )}
        </div>
      </Card>

      {/* Pending Invitations (Admin Only) */}
      {isAdmin && invitations.length > 0 && (
        <Card>
          <h3 className="section-title">Pending Invitations ({invitations.length})</h3>
          <div className="invitations-list">
            {invitations.map((inv) => (
              <div key={inv.id} className="invitation-item">
                <span className="invitation-phone">{inv.phone_number}</span>
                <span className="invitation-date">
                  {new Date(inv.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="stats-grid">
        <Card>
          <div className="stat-content">
            <span className="stat-label">Collected</span>
            <span className="stat-value">{formatCurrency(total_collected_current_round)}</span>
            <span className="stat-subtext">of {formatCurrency(totalExpected)}</span>
          </div>
        </Card>

        <Card>
          <div className="stat-content">
            <span className="stat-label">Members Paid</span>
            <span className="stat-value">
              {members.filter(m => m.paid_current_round).length} / {members.length}
            </span>
            <span className="stat-subtext">{progress.toFixed(0)}% complete</span>
          </div>
        </Card>
      </div>

      {/* Progress Bar */}
      <Card>
        <div className="progress-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
          <span className="progress-text">{progress.toFixed(0)}% of contributions received</span>
        </div>
      </Card>

      {/* Next Recipient Card */}
      {next_recipient && (
        <Card>
          <h3 className="section-title">Next Payout</h3>
          <div className="recipient-container">
            <div className="recipient-info">
              <div className="recipient-avatar">
                {next_recipient.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="recipient-name">{next_recipient.name}</div>
                <div className="recipient-position">Position {next_recipient.rotation_position}</div>
              </div>
            </div>
            <div className="recipient-amount">
              {formatCurrency(totalExpected)}
            </div>
          </div>
          {progress >= 100 && isAdmin && (
            <Button onClick={handleApprovePayout} loading={approving} fullWidth>
              Approve Payout
            </Button>
          )}
        </Card>
      )}

      {/* Members List */}
      <Card>
        <GroupMembersView
          members={members}
          currentUserId={currentUser?.id}
          groupId={group.id}
          contributionAmount={group.contribution_amount}
          currentRound={group.current_round}
          isAdmin={isAdmin}
          onPaymentSuccess={() => loadDashboard(true)}
        />
      </Card>

      {/* Invite Modal */}
      {inviteModalOpen && (
        <div className="modal-overlay" onClick={() => setInviteModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Invite Member</h2>
            <p className="modal-subtitle">
              Enter the phone number of the person you want to invite
            </p>
            
            <form onSubmit={handleInviteMember}>
              <Input
                label="Phone Number"
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+233244123456"
                fullWidth
                autoFocus
              />
              
              <p className="modal-helper">
                ℹ️ They will receive an SMS with the group code
              </p>

              <div className="modal-actions">
                <Button type="button" variant="outline" onClick={() => {
                  setPhoneNumber('');
                  setInviteModalOpen(false);
                }}>
                  Cancel
                </Button>
                <Button type="submit" loading={inviting}>
                  Send Invitation
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default GroupDashboardPage;

