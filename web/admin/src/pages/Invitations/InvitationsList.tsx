import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/adminClient';
import type { InvitationItem } from '../../types/admin';

export default function InvitationsList() {
  const [invitations, setInvitations] = useState<InvitationItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInvitations();
  }, []);

  const loadInvitations = async () => {
    try {
      const data = await adminAPI.getInvitations();
      setInvitations(data);
    } catch (error) {
      console.error('Failed to load invitations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1 className="page-title">Invitations</h1>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Group</th>
              <th>Phone Number</th>
              <th>Invited By</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {invitations.map((inv) => (
              <tr key={inv.id}>
                <td>{inv.id}</td>
                <td>{inv.group_name}</td>
                <td>{inv.phone_number}</td>
                <td>{inv.invited_by}</td>
                <td>
                  <span className={`badge badge-${
                    inv.status === 'accepted' ? 'success' :
                    inv.status === 'rejected' ? 'danger' :
                    inv.status === 'expired' ? 'secondary' : 'warning'
                  }`}>
                    {inv.status}
                  </span>
                </td>
                <td>{new Date(inv.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

