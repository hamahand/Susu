import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AppLayout } from './components/AppLayout';

// Lazy load pages
const LoginPage = React.lazy(() => import('./pages/LoginPage'));
const RegisterPage = React.lazy(() => import('./pages/RegisterPage'));
const OtpVerifyPage = React.lazy(() => import('./pages/OtpVerifyPage'));
const DashboardPage = React.lazy(() => import('./pages/DashboardPage'));
const CreateGroupPage = React.lazy(() => import('./pages/CreateGroupPage'));
const JoinGroupPage = React.lazy(() => import('./pages/JoinGroupPage'));
const GroupDashboardPage = React.lazy(() => import('./pages/GroupDashboardPage'));
const ProfilePage = React.lazy(() => import('./pages/ProfilePage'));

function App() {
  return (
    <BrowserRouter basename="/app">
      <AuthProvider>
        <React.Suspense fallback={<div className="loading-container">Loading...</div>}>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/otp-verify" element={<OtpVerifyPage />} />

            {/* Protected routes */}
            <Route
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/groups/create" element={<CreateGroupPage />} />
              <Route path="/groups/join" element={<JoinGroupPage />} />
              <Route path="/groups/:id" element={<GroupDashboardPage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Route>

            {/* Redirects */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </React.Suspense>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;

