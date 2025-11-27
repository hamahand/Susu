import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/adminClient';
import './DatabaseManager.css';

export default function DatabaseManager() {
  const [tables, setTables] = useState<any[]>([]);
  const [query, setQuery] = useState('SELECT * FROM users LIMIT 10');
  const [queryResult, setQueryResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadDatabaseInfo();
  }, []);

  const loadDatabaseInfo = async () => {
    try {
      const [tablesData, statsData] = await Promise.all([
        adminAPI.getDatabaseTables(),
        adminAPI.getDatabaseStats(),
      ]);
      setTables(tablesData.tables || []);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load database info:', error);
    }
  };

  const executeQuery = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const result = await adminAPI.executeDatabaseQuery(query);
      setQueryResult(result);
    } catch (error: any) {
      setQueryResult({
        error: error.message || 'Query failed'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="database-manager">
      <h1 className="page-title">Database Manager</h1>
      <div className="warning-message">
        ⚠️ This section is for Super Admins only. Proceed with caution.
      </div>

      <div className="database-sections">
        <div className="section-card">
          <div className="section-header">
            <h2>Database Tables</h2>
          </div>
          <div className="tables-list">
            {tables.map((table) => (
              <div key={table.name} className="table-item">
                <span className="table-name">{table.name}</span>
                <span className="table-count">{table.row_count} rows</span>
              </div>
            ))}
          </div>
        </div>

        <div className="section-card">
          <div className="section-header">
            <h2>SQL Query Executor</h2>
          </div>
          <textarea
            className="query-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="SELECT * FROM users LIMIT 10"
          />
          <button 
            className="btn btn-primary execute-btn"
            onClick={executeQuery}
            disabled={loading}
          >
            {loading ? 'Executing...' : 'Execute Query'}
          </button>
          
          {queryResult && (
            <div className="query-results">
              {queryResult.error ? (
                <div className="error-message">{queryResult.error}</div>
              ) : (
                <>
                  <div className="result-count">
                    {queryResult.count} row(s) returned
                  </div>
                  <div className="result-table">
                    <table>
                      <thead>
                        {queryResult.rows && queryResult.rows[0] && (
                          <tr>
                            {Object.keys(queryResult.rows[0]).map((key) => (
                              <th key={key}>{key}</th>
                            ))}
                          </tr>
                        )}
                      </thead>
                      <tbody>
                        {queryResult.rows && queryResult.rows.map((row: any, idx: number) => (
                          <tr key={idx}>
                            {Object.values(row).map((val: any, colIdx: number) => (
                              <td key={colIdx}>{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {stats && (
          <div className="section-card">
            <div className="section-header">
              <h2>Database Statistics</h2>
            </div>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Database:</span>
                <span className="stat-value">{stats.database_name}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Redis URL:</span>
                <span className="stat-value">{stats.redis_url}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Database URL:</span>
                <span className="stat-value">{stats.database_url}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

