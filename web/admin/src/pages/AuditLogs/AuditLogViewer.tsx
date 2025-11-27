import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/adminClient';
import type { AuditLogItem } from '../../types/admin';

export default function AuditLogViewer() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const data = await adminAPI.getAuditLogs({ limit: 100 });
      setLogs(data);
    } catch (error) {
      console.error('Failed to load audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1 className="page-title">Audit Logs</h1>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Entity Type</th>
              <th>Entity ID</th>
              <th>Action</th>
              <th>Performed By</th>
              <th>Timestamp</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{log.id}</td>
                <td><span className="badge badge-secondary">{log.entity_type}</span></td>
                <td>{log.entity_id || '-'}</td>
                <td><span className="badge badge-info">{log.action}</span></td>
                <td>{log.performed_by || 'System'}</td>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td style={{ fontSize: '0.75rem', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {log.details}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

