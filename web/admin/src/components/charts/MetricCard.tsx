import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon?: string;
  subtitle?: string;
  trend?: { value: number; isPositive: boolean };
}

export default function MetricCard({ title, value, icon, subtitle, trend }: MetricCardProps) {
  return (
    <div className="metric-card">
      <div className="metric-header">
        {icon && <span className="metric-icon">{icon}</span>}
        <h3 className="metric-title">{title}</h3>
      </div>
      <div className="metric-value">{value}</div>
      {subtitle && <div className="metric-subtitle">{subtitle}</div>}
      {trend && (
        <div className={`metric-trend ${trend.isPositive ? 'positive' : 'negative'}`}>
          {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
        </div>
      )}
    </div>
  );
}

