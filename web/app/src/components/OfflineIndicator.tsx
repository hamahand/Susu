import React from 'react';
import { useOnline } from '../hooks/useOnline';
import './OfflineIndicator.css';

export const OfflineIndicator: React.FC = () => {
  const isOnline = useOnline();

  if (isOnline) return null;

  return (
    <div className="offline-indicator">
      <span className="offline-indicator-icon">⚠️</span>
      <span className="offline-indicator-text">You are offline. Some features may be limited.</span>
    </div>
  );
};

