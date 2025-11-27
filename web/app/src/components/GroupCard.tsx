import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from './Card';
import { StatusBadge } from './StatusBadge';
import { Group, GroupStatus } from '../types/api';
import { formatCurrency } from '../utils/validation';
import './GroupCard.css';

interface GroupCardProps {
  group: Group;
}

export const GroupCard: React.FC<GroupCardProps> = ({ group }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/groups/${group.id}`);
  };

  return (
    <Card onClick={handleClick} className="group-card">
      <div className="group-card-header">
        <h3 className="group-card-name">{group.name}</h3>
        <StatusBadge status={group.status as GroupStatus} />
      </div>
      
      <div className="group-card-info">
        <div className="group-card-info-item">
          <span className="group-card-label">Contribution</span>
          <span className="group-card-value">{formatCurrency(group.contribution_amount)}</span>
        </div>
        <div className="group-card-info-item">
          <span className="group-card-label">Round</span>
          <span className="group-card-value">{group.current_round} / {group.num_cycles}</span>
        </div>
        <div className="group-card-info-item">
          <span className="group-card-label">Members</span>
          <span className="group-card-value">{group.member_count || 0}</span>
        </div>
      </div>
      
      <div className="group-card-footer">
        <span className="group-card-code">Code: {group.group_code}</span>
      </div>
    </Card>
  );
};

