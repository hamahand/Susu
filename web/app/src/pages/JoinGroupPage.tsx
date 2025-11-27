import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { groupService } from '../api/groupService';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import './JoinGroupPage.css';

const JoinGroupPage: React.FC = () => {
  const navigate = useNavigate();
  const [groupCode, setGroupCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!groupCode.trim()) {
      setError('Please enter a group code');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const result = await groupService.joinGroup({ group_code: groupCode.trim() });
      navigate(`/groups/${result.group_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to join group');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="join-group-page">
      <div className="join-group-container">
        <div className="join-group-header">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            ← Back
          </Button>
          <h1 className="join-group-title">Join a Group</h1>
          <p className="join-group-subtitle">
            Enter the group code shared by the group admin
          </p>
        </div>

        <div className="join-group-content">
          <Card>
            <form onSubmit={handleSubmit} className="join-group-form">
              {error && <div className="form-error">{error}</div>}

              <div className="join-group-icon">🔗</div>

              <Input
                label="Group Code"
                value={groupCode}
                onChange={(e) => setGroupCode(e.target.value.toUpperCase())}
                placeholder="e.g., ABC123XYZ"
                fullWidth
                autoFocus
              />

              <div className="join-group-info">
                <h4>💡 How to get a group code?</h4>
                <ul>
                  <li>Ask the group admin to share the group code</li>
                  <li>The code is usually 6-10 characters long</li>
                  <li>Check your SMS if you were invited</li>
                </ul>
              </div>

              <div className="form-actions">
                <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                  Cancel
                </Button>
                <Button type="submit" loading={loading}>
                  Join Group
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default JoinGroupPage;

