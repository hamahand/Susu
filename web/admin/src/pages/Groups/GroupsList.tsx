import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI } from '../../api/adminClient';
import type { GroupListItem } from '../../types/admin';

export default function GroupsList() {
  const [groups, setGroups] = useState<GroupListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const data = await adminAPI.getGroups();
      setGroups(data);
    } catch (error) {
      console.error('Failed to load groups:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1 className="page-title">Groups Management</h1>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Group Code</th>
              <th>Name</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Members</th>
              <th>Total Contributions</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {groups.map((group) => (
              <tr key={group.id}>
                <td>{group.id}</td>
                <td><strong>{group.group_code}</strong></td>
                <td>{group.name}</td>
                <td>GHS {group.contribution_amount}</td>
                <td>
                  <span className={`badge badge-${group.status === 'active' ? 'success' : 'secondary'}`}>
                    {group.status}
                  </span>
                </td>
                <td>{group.member_count}</td>
                <td>GHS {group.total_contributions.toFixed(2)}</td>
                <td>
                  <Link to={`/groups/${group.id}`} className="btn btn-outline" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

