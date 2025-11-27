import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { OfflineIndicator } from './OfflineIndicator';
import { InstallPrompt } from './InstallPrompt';
import './AppLayout.css';

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'My Groups', icon: '🏦' },
    { path: '/groups/create', label: 'Create Group', icon: '➕' },
    { path: '/groups/join', label: 'Join Group', icon: '🔗' },
    { path: '/profile', label: 'Profile', icon: '👤' },
  ];

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="app-header-container">
          <div className="app-header-left">
            <button className="mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
              <span className="hamburger"></span>
            </button>
            <h1 className="app-logo" onClick={() => navigate('/dashboard')}>
              SusuSave
            </h1>
          </div>
          
          <nav className={`app-nav ${menuOpen ? 'app-nav-open' : ''}`}>
            {navItems.map((item) => (
              <button
                key={item.path}
                className={`app-nav-item ${location.pathname === item.path ? 'active' : ''}`}
                onClick={() => {
                  navigate(item.path);
                  setMenuOpen(false);
                }}
              >
                <span className="app-nav-icon">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          <div className="app-header-right">
            {user && (
              <>
                <span className="app-user-name">{user.name}</span>
                <button className="app-logout-btn" onClick={handleLogout}>
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="app-content">
          <Outlet />
        </div>
      </main>

      <OfflineIndicator />
      <InstallPrompt />
    </div>
  );
};

