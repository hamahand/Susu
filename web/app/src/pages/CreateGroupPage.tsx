import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { groupService } from '../api/groupService';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import './CreateGroupPage.css';

const CreateGroupPage: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [contributionAmount, setContributionAmount] = useState('');
  const [numMembers, setNumMembers] = useState('');
  const [frequency, setFrequency] = useState<'weekly' | 'biweekly' | 'monthly'>('weekly');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errors, setErrors] = useState<{ 
    name?: string; 
    contributionAmount?: string; 
    numMembers?: string 
  }>({});

  const validate = () => {
    const newErrors: typeof errors = {};

    if (!name.trim() || name.trim().length < 3) {
      newErrors.name = 'Group name must be at least 3 characters';
    }

    const amount = parseFloat(contributionAmount);
    if (!contributionAmount || isNaN(amount) || amount <= 0) {
      newErrors.contributionAmount = 'Amount must be greater than 0';
    }

    const members = parseInt(numMembers);
    if (!numMembers || isNaN(members) || members < 2 || members > 50) {
      newErrors.numMembers = 'Number of members must be between 2 and 50';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setError('');
    try {
      const group = await groupService.createGroup({
        name: name.trim(),
        contribution_amount: parseFloat(contributionAmount),
        num_cycles: parseInt(numMembers), // Using numMembers as cycles for consistency
      });
      navigate(`/groups/${group.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create group');
    } finally {
      setLoading(false);
    }
  };

  const totalAmount = contributionAmount && numMembers ? parseFloat(contributionAmount) * parseInt(numMembers) : 0;
  const frequencyText = frequency === 'weekly' ? 'week' : frequency === 'biweekly' ? '2 weeks' : 'month';

  return (
    <div className="create-group-page">
      <div className="create-group-container">
        <div className="create-group-header">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            ← Back
          </Button>
          <h1 className="create-group-title">Create New Group</h1>
          <p className="create-group-subtitle">
            Set up a new savings group and invite members
          </p>
        </div>

        <div className="create-group-content">
          <Card>
            <form onSubmit={handleSubmit} className="create-group-form">
              {error && <div className="form-error">{error}</div>}

              <Input
                label="Group Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Weekly Savings Circle"
                error={errors.name}
                fullWidth
              />

              <Input
                label="Contribution Amount (GHS)"
                type="number"
                step="0.01"
                value={contributionAmount}
                onChange={(e) => setContributionAmount(e.target.value)}
                placeholder="50"
                error={errors.contributionAmount}
                fullWidth
              />

              <div className="frequency-selection">
                <label className="frequency-label">Contribution Frequency</label>
                <div className="frequency-buttons">
                  <button
                    type="button"
                    className={`frequency-btn ${frequency === 'weekly' ? 'active' : ''}`}
                    onClick={() => setFrequency('weekly')}
                  >
                    Weekly
                  </button>
                  <button
                    type="button"
                    className={`frequency-btn ${frequency === 'biweekly' ? 'active' : ''}`}
                    onClick={() => setFrequency('biweekly')}
                  >
                    Bi-weekly
                  </button>
                  <button
                    type="button"
                    className={`frequency-btn ${frequency === 'monthly' ? 'active' : ''}`}
                    onClick={() => setFrequency('monthly')}
                  >
                    Monthly
                  </button>
                </div>
              </div>

              <Input
                label="Number of Members"
                type="number"
                value={numMembers}
                onChange={(e) => setNumMembers(e.target.value)}
                placeholder="e.g., 10"
                error={errors.numMembers}
                helperText="Number of members determines the number of payout cycles"
                fullWidth
              />

              {/* Preview Card */}
              {contributionAmount && numMembers && (
                <div className="preview-card">
                  <h4 className="preview-title">Preview</h4>
                  <div className="preview-row">
                    <span className="preview-label">Contribution:</span>
                    <span className="preview-value">GHS {contributionAmount} / {frequencyText}</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">Members:</span>
                    <span className="preview-value">{numMembers} people</span>
                  </div>
                  <div className="preview-row">
                    <span className="preview-label">Rounds:</span>
                    <span className="preview-value">{numMembers} (one payout per member)</span>
                  </div>
                  <div className="preview-row preview-total">
                    <span className="preview-label">Total payout per member:</span>
                    <span className="preview-value total-value">
                      GHS {totalAmount.toFixed(2)}
                    </span>
                  </div>
                </div>
              )}

              <div className="form-actions">
                <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                  Cancel
                </Button>
                <Button type="submit" loading={loading}>
                  Create Group
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CreateGroupPage;

