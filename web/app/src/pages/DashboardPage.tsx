import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { groupService } from '../api/groupService';
import { Group } from '../types/api';
import { GroupCard } from '../components/GroupCard';
import { Button } from '../components/Button';
import { LoadingSpinner } from '../components/LoadingSpinner';
import './DashboardPage.css';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const data = await groupService.getMyGroups();
      setGroups(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load groups');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-loading">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">My Groups</h1>
          <p className="dashboard-subtitle">Manage your savings groups</p>
        </div>
        <div className="dashboard-actions">
          <Button onClick={() => navigate('/groups/create')}>
            ➕ Create Group
          </Button>
          <Button variant="outline" onClick={() => navigate('/groups/join')}>
            🔗 Join Group
          </Button>
        </div>
      </div>

      {error && <div className="dashboard-error">{error}</div>}

      {groups.length === 0 ? (
        <div className="dashboard-empty">
          <div className="dashboard-empty-icon">🏦</div>
          <h3 className="dashboard-empty-title">No groups yet</h3>
          <p className="dashboard-empty-text">
            Create your first savings group or join an existing one to get started
          </p>
          <div className="dashboard-empty-actions">
            <Button onClick={() => navigate('/groups/create')}>
              Create Your First Group
            </Button>
            <Button variant="outline" onClick={() => navigate('/groups/join')}>
              Join a Group
            </Button>
          </div>
        </div>
      ) : (
        <div className="dashboard-grid">
          {groups.map((group) => (
            <GroupCard key={group.id} group={group} />
          ))}
        </div>
      )}
    </div>
  );
};

export default DashboardPage;

