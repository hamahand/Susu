import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminAPI } from '../../api/adminClient';
import type { GroupDetail } from '../../types/admin';

export default function GroupDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [group, setGroup] = useState<GroupDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadGroup();
    }
  }, [id]);

  const loadGroup = async () => {
    try {
      const data = await adminAPI.getGroupDetail(Number(id));
      setGroup(data);
    } catch (error) {
      console.error('Failed to load group:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuspend = async () => {
    if (!confirm('Suspend this group?')) return;
    try {
      await adminAPI.suspendGroup(Number(id));
      loadGroup();
      alert('Group suspended');
    } catch (error: any) {
      alert('Failed: ' + error.message);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!group) return <div>Group not found</div>;

  return (
    <div>
      <button onClick={() => navigate('/groups')} className="btn btn-outline" style={{ marginBottom: '1rem' }}>
        ← Back
      </button>

      <h1 className="page-title">{group.name}</h1>

      <div className="card">
        <h2>Group Information</h2>
        <div style={{ display: 'grid', gap: '1rem', marginTop: '1rem' }}>
          <div><strong>Code:</strong> {group.group_code}</div>
          <div><strong>Contribution:</strong> GHS {group.contribution_amount}</div>
          <div><strong>Cycles:</strong> {group.num_cycles}</div>
          <div><strong>Current Round:</strong> {group.current_round}</div>
          <div><strong>Status:</strong> <span className="badge">{group.status}</span></div>
        </div>

        <h3 style={{ marginTop: '2rem' }}>Members ({group.members.length})</h3>
        <table style={{ marginTop: '1rem' }}>
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Position</th>
            </tr>
          </thead>
          <tbody>
            {group.members.map((member) => (
              <tr key={member.user_id}>
                <td>{member.name}</td>
                <td>{member.phone}</td>
                <td>{member.rotation_position}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {group.status === 'active' && (
          <button onClick={handleSuspend} className="btn btn-danger" style={{ marginTop: '2rem' }}>
            Suspend Group
          </button>
        )}
      </div>
    </div>
  );
}

