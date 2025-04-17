from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

class ConversationState(Enum):
    INITIAL = "initial"
    GATHERING_INFO = "gathering_info"
    CONFIRMING = "confirming"
    PROCESSING = "processing"
    FOLLOWING_UP = "following_up"
    COMPLETED = "completed"

@dataclass
class ConversationContext:
    user_id: str
    user_type: str
    current_state: ConversationState
    gathered_info: Dict[str, Any]
    pending_actions: List[str]
    history: List[Dict[str, Any]]

class EnhancedConversation:
    def __init__(self):
        self.active_conversations = {}
        self.flow_templates = self._load_flow_templates()
        self.fallback_handlers = self._initialize_fallback_handlers()
        self.analytics 