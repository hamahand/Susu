import { Link, useLocation } from 'react-router-dom';
import { useAdminAuth } from '../contexts/AdminAuthContext';
import './AdminLayout.css';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const { user, logout } = useAdminAuth();
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <div className="admin-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>SusuSave Admin</h1>
          <div className="admin-info">
            <span className="admin-name">{user?.name}</span>
            <span className="admin-role">{user?.admin_role?.replace('_', ' ')}</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <Link to="/" className={isActive('/') && !isActive('/users') && !isActive('/groups') ? 'active' : ''}>
            📊 Dashboard
          </Link>
          <Link to="/users" className={isActive('/users') ? 'active' : ''}>
            👥 Users
          </Link>
          <Link to="/groups" className={isActive('/groups') ? 'active' : ''}>
            👪 Groups
          </Link>
          <Link to="/payments" className={isActive('/payments') ? 'active' : ''}>
            💳 Payments
          </Link>
          <Link to="/payouts" className={isActive('/payouts') ? 'active' : ''}>
            💰 Payouts
          </Link>
          <Link to="/invitations" className={isActive('/invitations') ? 'active' : ''}>
            ✉️ Invitations
          </Link>
          <Link to="/settings" className={isActive('/settings') ? 'active' : ''}>
            ⚙️ Settings
          </Link>
          <Link to="/database" className={isActive('/database') ? 'active' : ''}>
            🗄️ Database
          </Link>
          <Link to="/audit-logs" className={isActive('/audit-logs') ? 'active' : ''}>
            📝 Audit Logs
          </Link>
        </nav>

        <div className="sidebar-footer">
          <button onClick={logout} className="btn btn-outline">
            🚪 Logout
          </button>
        </div>
      </aside>

      <main className="main-content">
        <div className="content-wrapper">{children}</div>
      </main>
    </div>
  );
}

