import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI } from '../../api/adminClient';
import type { UserListItem } from '../../types/admin';

export default function UsersList() {
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [userType, setUserType] = useState('');
  const [kycFilter, setKycFilter] = useState<string>('');

  useEffect(() => {
    loadUsers();
  }, [userType, kycFilter]);

  const loadUsers = async () => {
    try {
      const data = await adminAPI.getUsers({
        user_type: userType || undefined,
        kyc_verified: kycFilter === 'verified' ? true : kycFilter === 'pending' ? false : undefined,
        search: search || undefined,
      });
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadUsers();
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 className="page-title">Users Management</h1>
        <button onClick={() => adminAPI.exportUsers()} className="btn btn-outline">
          📥 Export CSV
        </button>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', alignItems: 'end' }}>
          <div style={{ flex: 1 }}>
            <label>Search by name</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search users..."
            />
          </div>
          
          <div style={{ width: '150px' }}>
            <label>User Type</label>
            <select value={userType} onChange={(e) => setUserType(e.target.value)}>
              <option value="">All Types</option>
              <option value="app">App Users</option>
              <option value="ussd">USSD Users</option>
            </select>
          </div>

          <div style={{ width: '150px' }}>
            <label>KYC Status</label>
            <select value={kycFilter} onChange={(e) => setKycFilter(e.target.value)}>
              <option value="">All</option>
              <option value="verified">Verified</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary">
            Search
          </button>
        </form>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Type</th>
                <th>KYC</th>
                <th>Admin</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.name}</td>
                  <td>{user.phone_number}</td>
                  <td>
                    <span className="badge badge-secondary">{user.user_type}</span>
                  </td>
                  <td>
                    {user.kyc_verified ? (
                      <span className="badge badge-success">Verified</span>
                    ) : (
                      <span className="badge badge-warning">Pending</span>
                    )}
                  </td>
                  <td>
                    {user.is_system_admin && (
                      <span className="badge badge-info">{user.admin_role}</span>
                    )}
                  </td>
                  <td>{new Date(user.created_at).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/users/${user.id}`} className="btn btn-outline" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {users.length === 0 && (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No users found
            </div>
          )}
        </div>
      )}
    </div>
  );
}

