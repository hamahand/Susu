import React, { useState, useMemo } from 'react';
import { GroupMember } from '../types/api';
import { StatusBadge } from './StatusBadge';
import { PaymentButton } from './PaymentButton';
import { formatCurrency } from '../utils/validation';
import './GroupMembersView.css';

// Simple icon for the header (Lucide 'Users' equivalent)
const UsersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 h-6 w-6 text-emerald-600">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
);

// Simple icon for the button (Lucide 'DollarSign' equivalent)
const DollarSignIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2 h-4 w-4">
    <line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
  </svg>
);

// Simple icon for the search bar (Lucide 'Search' equivalent)
const SearchIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 text-slate-400">
    <circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/>
  </svg>
);

interface GroupMembersViewProps {
  members: GroupMember[];
  currentUserId?: number;
  groupId: number;
  contributionAmount: number;
  currentRound: number;
  isAdmin: boolean;
  onPaymentSuccess?: () => void;
}

const GroupMembersView: React.FC<GroupMembersViewProps> = ({
  members,
  currentUserId,
  groupId,
  contributionAmount,
  currentRound,
  isAdmin,
  onPaymentSuccess
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Filtering logic using useMemo for performance
  const filteredMembers = useMemo(() => {
    if (!searchTerm) {
      return members;
    }
    const lowercasedTerm = searchTerm.toLowerCase();
    return members.filter(member =>
      member.display_name.toLowerCase().includes(lowercasedTerm) ||
      member.phone_number.includes(searchTerm)
    );
  }, [members, searchTerm]);

  const MemberCard = ({ member, index }: { member: GroupMember; index: number }) => {
    const isPaid = member.paid_current_round;
    const isCurrentUser = currentUserId === member.user_id;
    const isOwner = member.is_admin;
    
    // Determine the style for the status badge
    const statusClasses = isPaid
      ? 'bg-emerald-100 text-emerald-700'
      : 'bg-red-100 text-red-700';

    // Determine the style for the main card (highlighting 'You' and 'Owner')
    let cardClasses = 'bg-white hover:bg-gray-50';
    if (isCurrentUser) {
        cardClasses = 'border-2 border-emerald-500 bg-emerald-50 shadow-md';
    } else if (isOwner) {
        // Subtle gold/owner highlight
        cardClasses = 'border-2 border-amber-300 bg-amber-50 hover:bg-amber-100 shadow-sm';
    }

    return (
      <div
        className={`flex items-center justify-between p-4 rounded-xl transition duration-300 mb-3 cursor-pointer ${cardClasses}`}
        role="listitem"
        aria-label={`Member ${index + 1}: ${member.display_name}, status ${member.paid_current_round ? 'paid' : 'unpaid'}`}
      >
        {/* Left Section: Index, Name, Phone */}
        <div className="flex items-center min-w-0 flex-1">
          {/* Rank/Index Circle */}
          <div
            className={`w-9 h-9 flex items-center justify-center rounded-full text-md font-bold mr-4 flex-shrink-0
              ${isCurrentUser ? 'bg-emerald-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            {member.rotation_position}
          </div>
          
          <div className="min-w-0">
            {/* Name and Tags */}
            <p className="text-lg font-semibold text-slate-800 flex items-center truncate">
              <span className="truncate">{member.display_name}</span>
              {member.alias && (
                <span className="ml-2 text-sm text-slate-500 italic">
                  ({member.alias})
                </span>
              )}
              {isOwner && <span className="ml-2 text-xl flex-shrink-0">👑</span>}
              {isCurrentUser && (
                <span className="ml-2 text-xs font-medium text-emerald-600 bg-emerald-200 px-2 py-0.5 rounded-full flex-shrink-0">
                  You
                </span>
              )}
            </p>
            {/* Phone Number */}
            <p className="text-sm text-slate-500 font-mono truncate">{member.phone_number}</p>
          </div>
        </div>

        {/* Right Section: Status and Action Button */}
        <div className="flex items-center space-x-4 flex-shrink-0 ml-4">
          {/* Status Badge */}
          <span
            className={`text-xs font-semibold px-3 py-1.5 rounded-full uppercase tracking-wider ${statusClasses}`}
          >
            {isPaid ? 'PAID' : 'UNPAID'}
          </span>

          {/* Action Button: Visible only for the current user and if unpaid */}
          {!isPaid && (isCurrentUser || (isAdmin && !isCurrentUser)) && (
            <PaymentButton
              groupId={groupId}
              userId={member.user_id}
              roundNumber={currentRound}
              amount={contributionAmount}
              memberName={member.display_name}
              isAdmin={isAdmin && !isCurrentUser}
              isCurrentUser={isCurrentUser}
              onSuccess={onPaymentSuccess}
            />
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="group-members-view">
      {/* Header and Search */}
      <div className="border-b pb-4 mb-6">
        <div className="flex items-center mb-4">
          <UsersIcon />
          <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Group Members ({filteredMembers.length} / {members.length})
          </h3>
        </div>

        {/* Search Input */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search by name or phone number..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-emerald-500 focus:border-emerald-500 placeholder-slate-400 text-slate-700"
            aria-label="Search members"
          />
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
            <SearchIcon />
          </div>
        </div>
      </div>

      {/* Member List Container (Fixed Height for Scrollability) */}
      <div 
        role="list" 
        className="space-y-3 max-h-[60vh] overflow-y-auto pr-2"
        style={{ scrollbarGutter: 'stable' }} // Prevents content shift when scrollbar appears
      >
        {filteredMembers.length > 0 ? (
          filteredMembers.map((member, index) => (
            <MemberCard key={member.user_id} member={member} index={index} />
          ))
        ) : (
          <div className="text-center py-10 text-slate-500">
            No members found matching "{searchTerm}".
          </div>
        )}
      </div>
      
      {/* Footer for list length visibility */}
      <div className="mt-4 pt-4 border-t text-sm text-slate-500 text-center">
        List End. Showing {filteredMembers.length} of {members.length} total members.
      </div>
    </div>
  );
};

export default GroupMembersView;
