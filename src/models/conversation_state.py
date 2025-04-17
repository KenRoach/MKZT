from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

class ConversationState(str, Enum):
    # Initial States
    GREETING = "greeting"
    MENU_BROWSING = "menu_browsing"
    ITEM_SELECTION = "item_selection"
    CUSTOMIZATION = "customization"
    
    # Order States
    ORDER_CONFIRMATION = "order_confirmation"
    PAYMENT_SELECTION = "payment_selection"
    PAYMENT_PROCESSING = "payment_processing"
    PAYMENT_CONFIRMED = "payment_confirmed"
    
    # Kitchen States
    KITCHEN_QUEUE = "kitchen_queue"
    KITCHEN_PREPARING = "kitchen_preparing"
    KITCHEN_READY = "kitchen_ready"
    
    # Delivery States
    DRIVER_ASSIGNMENT = "driver_assignment"
    DRIVER_PICKUP = "driver_pickup"
    DRIVER_ENROUTE = "driver_enroute"
    DELIVERY_ARRIVING = "delivery_arriving"
    DELIVERED = "delivered"
    
    # Follow-up States
    FEEDBACK_REQUEST = "feedback_request"
    ISSUE_RESOLUTION = "issue_resolution"
    COMPLETED = "completed"

class StateTransition(BaseModel):
    from_state: ConversationState
    to_state: ConversationState
    conditions: Dict[str, any]
    priority: int = 0
    
    def check_conditions(self, context: Dict) -> bool:
        """Check if all conditions are met for this transition"""
        for condition, value in self.conditions.items():
            if context.get(condition) != value:
                return False
        return True

class ConversationStateManager:
    def __init__(self):
        self.transitions = self._define_transitions()
        self.state_handlers = self._define_state_handlers()

    def _define_transitions(self) -> List[StateTransition]:
        """Define all possible state transitions"""
        return [
            StateTransition(
                from_state=ConversationState.GREETING,
                to_state=ConversationState.MENU_BROWSING,
                conditions={"menu_requested": True},
                priority=1
            ),
            StateTransition(
                from_state=ConversationState.MENU_BROWSING,
                to_state=ConversationState.ITEM_SELECTION,
                conditions={"item_selected": True},
                priority=1
            ),
            # Add more transitions...
        ]

    def _define_state_handlers(self) -> Dict:
        """Define handlers for each state"""
        return {
            ConversationState.GREETING: self._handle_greeting,
            ConversationState.MENU_BROWSING: self._handle_menu_browsing,
            ConversationState.ITEM_SELECTION: self._handle_item_selection,
            # Add more handlers...
        }

    async def get_next_state(self, current_state: ConversationState, context: Dict) -> ConversationState:
        """Determine the next state based on current state and context"""
        valid_transitions = [
            t for t in self.transitions 
            if t.from_state == current_state and t.check_conditions(context)
        ]
        
        if not valid_transitions:
            return current_state
            
        # Sort by priority and return highest priority transition
        return sorted(valid_transitions, key=lambda t: t.priority, reverse=True)[0].to_state

    async def handle_state(self, state: ConversationState, context: Dict) -> Dict:
        """Handle the current state"""
        handler = self.state_handlers.get(state)
        if handler:
            return await handler(context)
        return context

    async def _handle_greeting(self, context: Dict) -> Dict:
        """Handle greeting state"""
        # Implementation for greeting state
        pass

    async def _handle_menu_browsing(self, context: Dict) -> Dict:
        """Handle menu browsing state"""
        # Implementation for menu browsing state
        pass

    async def _handle_item_selection(self, context: Dict) -> Dict:
        """Handle item selection state"""
        # Implementation for item selection state
        pass

state_manager = ConversationStateManager() 