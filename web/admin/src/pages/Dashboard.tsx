import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI } from '../api/adminClient';
import type { DashboardStats, ActivityItem } from '../types/admin';
import LineChart from '../components/charts/LineChart';
import AreaChart from '../components/charts/AreaChart';
import PieChart from '../components/charts/PieChart';
import BarChart from '../components/charts/BarChart';
import MetricCard from '../components/charts/MetricCard';
import '../components/charts/charts.css';
import './Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsData, activityData, analyticsData] = await Promise.all([
        adminAPI.getDashboardStats(),
        adminAPI.getDashboardActivity(15),
        adminAPI.getAnalyticsOverview(),
      ]);
      setStats(statsData);
      setActivity(activityData);
      setAnalytics(analyticsData);
      
      // Prepare chart data
      if (analyticsData?.time_series) {
        setChartData({
          revenue: analyticsData.time_series.map((point: any) => ({
            date: point.date,
            value: point.revenue
          })),
          transactions: analyticsData.time_series.map((point: any) => ({
            date: point.date,
            value: point.total_transactions
          }))
        });
      }
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="dashboard">
      <h1 className="page-title">Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>Total Users</h3>
            <p className="stat-value">{stats?.total_users || 0}</p>
            <span className="stat-subtitle">{stats?.active_users || 0} active</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">👪</div>
          <div className="stat-content">
            <h3>Total Groups</h3>
            <p className="stat-value">{stats?.total_groups || 0}</p>
            <span className="stat-subtitle">{stats?.active_groups || 0} active</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h3>Total Revenue</h3>
            <p className="stat-value">GHS {stats?.total_revenue.toFixed(2) || '0.00'}</p>
            <span className="stat-subtitle">All time</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <h3>Pending Actions</h3>
            <p className="stat-value">
              {(stats?.pending_payments || 0) + (stats?.pending_payouts || 0)}
            </p>
            <span className="stat-subtitle">
              {stats?.pending_payments || 0} payments, {stats?.pending_payouts || 0} payouts
            </span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>KYC Verified</h3>
            <p className="stat-value">{stats?.kyc_verified || 0}</p>
            <span className="stat-subtitle">{stats?.kyc_pending || 0} pending</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">❌</div>
          <div className="stat-content">
            <h3>Failed Payments</h3>
            <p className="stat-value">{stats?.failed_payments || 0}</p>
            <span className="stat-subtitle">Need review</span>
          </div>
        </div>
      </div>

      {/* Chart Visualizations */}
      {chartData && (
        <div className="charts-section">
          <div className="section-card">
            <div className="section-header">
              <h2>Revenue Trends</h2>
            </div>
            <LineChart data={chartData.revenue} title="Revenue Over Time" color="#10b981" />
          </div>
          
          <div className="section-card">
            <div className="section-header">
              <h2>Transaction Volume</h2>
            </div>
            <AreaChart data={chartData.transactions} title="Transaction Volume" color="#3b82f6" />
          </div>
        </div>
      )}

      {/* Growth Metrics */}
      {analytics?.growth && (
        <div className="growth-metrics">
          <MetricCard
            title="Month-over-Month Growth"
            value={`${analytics.growth.mom_growth_percent}%`}
            icon="📈"
            subtitle="Revenue Growth"
          />
          <MetricCard
            title="Year-over-Year Growth"
            value={`${analytics.growth.yoy_growth_percent}%`}
            icon="📊"
            subtitle="Revenue Growth"
          />
        </div>
      )}

      <div className="dashboard-sections">
        <div className="section-card">
          <div className="section-header">
            <h2>Quick Actions</h2>
          </div>
          <div className="quick-actions">
            <Link to="/users" className="action-btn">
              👥 Manage Users
            </Link>
            <Link to="/groups" className="action-btn">
              👪 Manage Groups
            </Link>
            <Link to="/payments" className="action-btn">
              💳 View Payments
            </Link>
            <Link to="/payouts" className="action-btn">
              💰 Review Payouts
            </Link>
            <Link to="/settings" className="action-btn">
              ⚙️ System Settings
            </Link>
            <Link to="/audit-logs" className="action-btn">
              📝 Audit Logs
            </Link>
          </div>
        </div>

        <div className="section-card">
          <div className="section-header">
            <h2>Recent Activity</h2>
          </div>
          <div className="activity-list">
            {activity.length === 0 ? (
              <p className="no-data">No recent activity</p>
            ) : (
              activity.map((item, index) => (
                <div key={index} className="activity-item">
                  <div className="activity-icon">
                    {item.type === 'user_registration' && '👤'}
                    {item.type === 'group_creation' && '👪'}
                    {item.type === 'payment' && '💳'}
                  </div>
                  <div className="activity-content">
                    <p>{item.description}</p>
                    <span className="activity-time">
                      {new Date(item.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

