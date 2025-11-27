import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AdminAuthProvider, useAdminAuth } from './contexts/AdminAuthContext';
import AdminLogin from './pages/AdminLogin';
import Dashboard from './pages/Dashboard';
import UsersList from './pages/Users/UsersList';
import UserDetail from './pages/Users/UserDetail';
import GroupsList from './pages/Groups/GroupsList';
import GroupDetail from './pages/Groups/GroupDetail';
import PaymentsList from './pages/Payments/PaymentsList';
import PayoutsList from './pages/Payouts/PayoutsList';
import InvitationsList from './pages/Invitations/InvitationsList';
import SystemSettings from './pages/Settings/SystemSettings';
import AdminManagement from './pages/Settings/AdminManagement';
import AuditLogViewer from './pages/AuditLogs/AuditLogViewer';
import DatabaseManager from './pages/Database/DatabaseManager';
import AdminLayout from './components/AdminLayout';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAdminAuth();

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function AppRoutes() {
  const { isAuthenticated } = useAdminAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" /> : <AdminLogin />}
      />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <AdminLayout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/users" element={<UsersList />} />
                <Route path="/users/:id" element={<UserDetail />} />
                <Route path="/groups" element={<GroupsList />} />
                <Route path="/groups/:id" element={<GroupDetail />} />
                <Route path="/payments" element={<PaymentsList />} />
                <Route path="/payouts" element={<PayoutsList />} />
                <Route path="/invitations" element={<InvitationsList />} />
                <Route path="/settings" element={<SystemSettings />} />
                <Route path="/settings/admins" element={<AdminManagement />} />
                <Route path="/database" element={<DatabaseManager />} />
                <Route path="/audit-logs" element={<AuditLogViewer />} />
              </Routes>
            </AdminLayout>
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AdminAuthProvider>
        <AppRoutes />
      </AdminAuthProvider>
    </BrowserRouter>
  );
}

export default App;

