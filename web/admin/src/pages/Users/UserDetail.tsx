import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminAPI } from '../../api/adminClient';
import type { UserDetail } from '../../types/admin';

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    if (id) {
      loadUser();
    }
  }, [id]);

  const loadUser = async () => {
    try {
      const data = await adminAPI.getUserDetail(Number(id));
      setUser(data);
      setName(data.name);
      setEmail(data.email || '');
    } catch (error) {
      console.error('Failed to load user:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      await adminAPI.updateUser(Number(id), { name, email: email || undefined });
      setEditing(false);
      loadUser();
      alert('User updated successfully');
    } catch (error: any) {
      alert('Failed to update user: ' + error.message);
    }
  };

  const handleVerifyKYC = async () => {
    if (!confirm('Manually verify this user\'s KYC?')) return;
    try {
      await adminAPI.verifyUserKYC(Number(id));
      loadUser();
      alert('KYC verified successfully');
    } catch (error: any) {
      alert('Failed to verify KYC: ' + error.message);
    }
  };

  const handleDeactivate = async () => {
    if (!confirm('Deactivate this user? This will remove them from all groups.')) return;
    try {
      await adminAPI.deactivateUser(Number(id));
      alert('User deactivated');
      navigate('/users');
    } catch (error: any) {
      alert('Failed to deactivate user: ' + error.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div>
      <button onClick={() => navigate('/users')} className="btn btn-outline" style={{ marginBottom: '1rem' }}>
        ← Back to Users
      </button>

      <h1 className="page-title">User Details</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h2 style={{ marginBottom: '1.5rem' }}>Information</h2>

          {editing ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label>Name</label>
                <input value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div>
                <label>Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button onClick={handleUpdate} className="btn btn-primary">Save</button>
                <button onClick={() => setEditing(false)} className="btn btn-outline">Cancel</button>
              </div>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div>
                <strong>ID:</strong> {user.id}
              </div>
              <div>
                <strong>Name:</strong> {user.name}
              </div>
              <div>
                <strong>Phone:</strong> {user.phone_number}
              </div>
              <div>
                <strong>Email:</strong> {user.email || 'Not provided'}
              </div>
              <div>
                <strong>User Type:</strong> <span className="badge badge-secondary">{user.user_type}</span>
              </div>
              <div>
                <strong>KYC Status:</strong>{' '}
                {user.kyc_verified ? (
                  <span className="badge badge-success">Verified</span>
                ) : (
                  <span className="badge badge-warning">Pending</span>
                )}
              </div>
              <div>
                <strong>Created:</strong> {new Date(user.created_at).toLocaleString()}
              </div>
              <div>
                <strong>Last Login:</strong> {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
              </div>

              <button onClick={() => setEditing(true)} className="btn btn-primary" style={{ marginTop: '1rem' }}>
                Edit Information
              </button>
            </div>
          )}
        </div>

        <div>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Statistics</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div>
                <strong>Total Groups:</strong> {user.total_groups}
              </div>
              <div>
                <strong>Active Memberships:</strong> {user.active_memberships}
              </div>
              <div>
                <strong>Total Payments:</strong> GHS {user.total_payments.toFixed(2)}
              </div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Actions</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {!user.kyc_verified && (
                <button onClick={handleVerifyKYC} className="btn btn-success">
                  ✓ Verify KYC
                </button>
              )}
              <button onClick={handleDeactivate} className="btn btn-danger">
                Deactivate User
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

