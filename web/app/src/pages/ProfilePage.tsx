import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { validateEmail } from '../utils/validation';
import './ProfilePage.css';

const ProfilePage: React.FC = () => {
  const { user, updateProfile, logout } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [errors, setErrors] = useState<{ name?: string; email?: string }>({});

  const validate = () => {
    const newErrors: typeof errors = {};

    if (!name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (email && !validateEmail(email)) {
      newErrors.email = 'Enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await updateProfile({
        username: name.trim(),
        email: email.trim() || undefined,
      });
      setSuccess('Profile updated successfully!');
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      logout();
      navigate('/login');
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <h1 className="profile-title">Profile Settings</h1>
          <p className="profile-subtitle">Manage your account information</p>
        </div>

        <div className="profile-content">
          {/* Profile Info Card */}
          <Card>
            <div className="profile-avatar-section">
              <div className="profile-avatar">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="profile-info">
                <h3>{user.name}</h3>
                <p className="profile-phone">{user.phone_number}</p>
                <p className="profile-type">Account Type: {user.user_type.toUpperCase()}</p>
              </div>
            </div>
          </Card>

          {/* Edit Profile Form */}
          <Card>
            <h3 className="section-title">Edit Profile</h3>
            <form onSubmit={handleSubmit} className="profile-form">
              {error && <div className="form-error">{error}</div>}
              {success && <div className="form-success">{success}</div>}

              <Input
                label="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                error={errors.name}
                fullWidth
              />

              <Input
                label="Email (Optional)"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@example.com"
                error={errors.email}
                fullWidth
              />

              <Input
                label="Phone Number"
                value={user.phone_number}
                disabled
                fullWidth
                helperText="Phone number cannot be changed"
              />

              <Button type="submit" loading={loading} fullWidth>
                Update Profile
              </Button>
            </form>
          </Card>

          {/* Account Actions */}
          <Card>
            <h3 className="section-title">Account Actions</h3>
            <div className="profile-actions">
              <Button variant="outline" onClick={() => navigate('/dashboard')} fullWidth>
                Back to Dashboard
              </Button>
              <Button variant="outline" onClick={handleLogout} fullWidth className="logout-btn-danger">
                Logout
              </Button>
            </div>
          </Card>

          {/* Account Info */}
          <Card>
            <h3 className="section-title">Account Information</h3>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">User ID</span>
                <span className="info-value">{user.id}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Member Since</span>
                <span className="info-value">
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;

