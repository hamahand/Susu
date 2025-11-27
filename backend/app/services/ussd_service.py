from typing import Dict, Optional
from sqlalchemy.orm import Session

from ..models import User, Group, Membership, UserType
from ..utils import encrypt_field, decrypt_field
from .group_service import GroupService
from .payment_service import PaymentService


class USSDSession:
    """In-memory USSD session storage (use Redis in production)."""
    sessions: Dict[str, Dict] = {}
    
    @classmethod
    def get(cls, session_id: str) -> Dict:
        """Get session data."""
        return cls.sessions.get(session_id, {})
    
    @classmethod
    def set(cls, session_id: str, data: Dict):
        """Set session data."""
        cls.sessions[session_id] = data
    
    @classmethod
    def clear(cls, session_id: str):
        """Clear session data."""
        if session_id in cls.sessions:
            del cls.sessions[session_id]


class USSDService:
    """Service for handling USSD interactions."""
    
    @staticmethod
    def handle_ussd_request(
        db: Session,
        session_id: str,
        phone_number: str,
        text: str,
        service_code: str = ""
    ) -> str:
        """
        Handle USSD request from AfricaTalking.
        
        Args:
            db: Database session
            session_id: USSD session ID
            phone_number: User's phone number
            text: User's input text
            service_code: USSD service code dialed
            
        Returns:
            USSD response string (CON for continue, END to end session)
        """
        try:
            # Get or create user
            user = USSDService._get_or_create_user(db, phone_number)
            
            # Parse input (AfricaTalking concatenates inputs with *)
            inputs = text.split('*') if text else []
            
            # Get session data
            session = USSDSession.get(session_id)
            
            # Main menu (when text is empty, it's the first request)
            if not text:
                return USSDService._main_menu()
            
            # Handle main menu selection
            if len(inputs) == 1:
                choice = inputs[0]
                
                if choice == '1':
                    # Join Group
                    USSDSession.set(session_id, {'action': 'join_group'})
                    return "CON Enter Group Code (e.g., SUSU1234):"
                
                elif choice == '2':
                    # Pay Contribution
                    USSDSession.set(session_id, {'action': 'pay_contribution'})
                    return USSDService._pay_contribution_menu(db, user, session_id)
                
                elif choice == '3':
                    # Check Balance/Status
                    return USSDService._check_status(db, user)
                
                elif choice == '4':
                    # My Payout Date
                    return USSDService._my_payout_date(db, user)
                
                elif choice == '5':
                    # Create Group
                    USSDSession.set(session_id, {'action': 'create_group'})
                    return "CON Enter Group Name:"
                
                elif choice == '6':
                    # Browse Groups
                    return USSDService._browse_groups(db)
                
                else:
                    return "END Invalid option. Please try again."
            
            # Handle sub-menus
            if len(inputs) == 2:
                action = session.get('action')
                
                if action == 'join_group':
                    group_code = inputs[1].upper()
                    result = USSDService._join_group(db, user, group_code)
                    # Clear session after completion
                    USSDSession.clear(session_id)
                    return result
                
                elif action == 'pay_contribution':
                    try:
                        group_index = int(inputs[1]) - 1
                        groups = session.get('groups', [])
                        
                        if group_index < 0 or group_index >= len(groups):
                            USSDSession.clear(session_id)
                            return "END Invalid group selection."
                        
                        result = USSDService._process_payment(db, user, groups[group_index])
                        # Clear session after completion
                        USSDSession.clear(session_id)
                        return result
                        
                    except (ValueError, IndexError):
                        USSDSession.clear(session_id)
                        return "END Invalid input. Please try again."
                
                elif action == 'create_group':
                    group_name = inputs[1]
                    USSDSession.set(session_id, {'action': 'create_group_amount', 'group_name': group_name})
                    return "CON Enter contribution amount (e.g., 100):"
                
                elif action == 'create_group_amount':
                    try:
                        amount = float(inputs[1])
                        group_name = session.get('group_name', 'My Group')
                        result = USSDService._create_group(db, user, group_name, amount)
                        # Clear session after completion
                        USSDSession.clear(session_id)
                        return result
                    except ValueError:
                        USSDSession.clear(session_id)
                        return "END Invalid amount. Please try again."
            
            # Handle 3-step inputs (for group creation)
            if len(inputs) == 3:
                action = session.get('action')
                
                if action == 'create_group_amount':
                    try:
                        amount = float(inputs[2])
                        group_name = session.get('group_name', 'My Group')
                        result = USSDService._create_group(db, user, group_name, amount)
                        # Clear session after completion
                        USSDSession.clear(session_id)
                        return result
                    except ValueError:
                        USSDSession.clear(session_id)
                        return "END Invalid amount. Please try again."
            
            # Clear session and return error for unknown inputs
            USSDSession.clear(session_id)
            return "END Invalid input. Please try again."
            
        except Exception as e:
            # Log error and return user-friendly message
            print(f"USSD Error: {str(e)}")  # In production, use proper logging
            USSDSession.clear(session_id)
            return "END An error occurred. Please try again later."
    
    @staticmethod
    def _get_or_create_user(db: Session, phone_number: str) -> User:
        """Get or create USSD user."""
        encrypted_phone = encrypt_field(phone_number)
        user = db.query(User).filter(User.phone_number == encrypted_phone).first()
        
        if not user:
            # Create new USSD user
            user = User(
                phone_number=encrypted_phone,
                name=f"User {phone_number[-4:]}",
                user_type=UserType.USSD,
                momo_account_id=encrypted_phone
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Log new user creation
            print(f"New USSD user created: {phone_number}")
        
        return user
    
    @staticmethod
    def _main_menu() -> str:
        """Return main USSD menu."""
        return (
            "CON Welcome to SusuSave\n"
            "1. Join Group\n"
            "2. Pay Contribution\n"
            "3. Check Balance/Status\n"
            "4. My Payout Date\n"
            "5. Create Group\n"
            "6. Browse Groups"
        )
    
    @staticmethod
    def _join_group(db: Session, user: User, group_code: str) -> str:
        """Handle joining a group."""
        try:
            membership = GroupService.join_group(db, group_code, user)
            group = membership.group
            
            return (
                f"END Success! You joined {group.name}.\n"
                f"Position: {membership.rotation_position}\n"
                f"Contribution: GHS {group.contribution_amount}\n"
                f"You will receive an SMS with details."
            )
        
        except Exception as e:
            return f"END Error: {str(e)}"
    
    @staticmethod
    def _pay_contribution_menu(db: Session, user: User, session_id: str) -> str:
        """Show groups for payment selection."""
        groups = GroupService.get_user_groups(db, user.id)
        
        if not groups:
            return "END You are not a member of any group. Join a group first."
        
        menu = "CON Select group to pay:\n"
        for idx, group in enumerate(groups, 1):
            menu += f"{idx}. {group.name} (GHS {group.contribution_amount})\n"
        
        # Store groups in session for later reference
        session_data = USSDSession.get(session_id)
        session_data['groups'] = groups
        USSDSession.set(session_id, session_data)
        
        return menu
    
    @staticmethod
    def _process_payment(db: Session, user: User, group: Group) -> str:
        """Process a payment."""
        try:
            payment = PaymentService.process_payment(
                db=db,
                user_id=user.id,
                group_id=group.id
            )
            
            return (
                f"END Payment successful!\n"
                f"Amount: GHS {payment.amount}\n"
                f"Group: {group.name}\n"
                f"Round: {payment.round_number}\n"
                f"You will receive SMS confirmation."
            )
        
        except Exception as e:
            return f"END Payment failed: {str(e)}"
    
    @staticmethod
    def _check_status(db: Session, user: User) -> str:
        """Check user's status across all groups."""
        groups = GroupService.get_user_groups(db, user.id)
        
        if not groups:
            return "END You are not a member of any group."
        
        status = "END Your Status:\n"
        
        for group in groups:
            membership = db.query(Membership).filter(
                Membership.user_id == user.id,
                Membership.group_id == group.id
            ).first()
            
            status += f"\n{group.name}:\n"
            status += f"- Position: {membership.rotation_position}/{group.num_cycles}\n"
            status += f"- Round: {group.current_round}/{group.num_cycles}\n"
            status += f"- Contribution: GHS {group.contribution_amount}\n"
        
        return status
    
    @staticmethod
    def _my_payout_date(db: Session, user: User) -> str:
        """Show user's payout information."""
        groups = GroupService.get_user_groups(db, user.id)
        
        if not groups:
            return "END You are not a member of any group."
        
        info = "END Your Payout Info:\n"
        
        for group in groups:
            membership = db.query(Membership).filter(
                Membership.user_id == user.id,
                Membership.group_id == group.id
            ).first()
            
            info += f"\n{group.name}:\n"
            
            if membership.rotation_position == group.current_round:
                info += "- YOU ARE NEXT TO RECEIVE!\n"
                info += f"- Amount: GHS {group.contribution_amount * len(GroupService.get_group_members(db, group.id, group.current_round))}\n"
            elif membership.rotation_position < group.current_round:
                info += "- Already received payout\n"
            else:
                rounds_until = membership.rotation_position - group.current_round
                info += f"- Your turn in {rounds_until} round(s)\n"
                info += f"- Expected: GHS {group.contribution_amount * len(GroupService.get_group_members(db, group.id, group.current_round))}\n"
        
        return info
    
    @staticmethod
    def _create_group(db: Session, user: User, group_name: str, contribution_amount: float) -> str:
        """Create a new group via USSD."""
        try:
            from ..schemas import GroupCreate
            from .group_service import GroupService
            
            # Create group data
            group_data = GroupCreate(
                name=group_name,
                contribution_amount=contribution_amount,
                num_cycles=12,  # Default to 12 months
                cash_only=False
            )
            
            # Create the group
            group = GroupService.create_group(db, group_data, user)
            
            return (
                f"END Group created successfully!\n"
                f"Name: {group.name}\n"
                f"Code: {group.group_code}\n"
                f"Contribution: GHS {group.contribution_amount}\n"
                f"You are the admin. Share the code with friends!"
            )
        
        except Exception as e:
            return f"END Failed to create group: {str(e)}"
    
    @staticmethod
    def _browse_groups(db: Session) -> str:
        """Browse available groups to join."""
        try:
            # Get active groups with space for more members
            groups = db.query(Group).filter(
                Group.status == 'active'
            ).limit(10).all()
            
            if not groups:
                return "END No groups available to join at the moment."
            
            menu = "CON Available Groups:\n"
            for idx, group in enumerate(groups[:5], 1):  # Show max 5 groups
                menu += f"{idx}. {group.name}\n"
                menu += f"   Code: {group.group_code}\n"
                menu += f"   Amount: GHS {group.contribution_amount}\n"
            
            menu += "\nUse option 1 to join with group code"
            return menu
        
        except Exception as e:
            return f"END Error browsing groups: {str(e)}"

