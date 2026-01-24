"""
Voice Gateway - Data Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


# ============================================
# Enums
# ============================================

class CallMode(str, Enum):
    AI = "ai"
    HUMAN = "human"
    TRANSFER = "transfer"


class CallStatus(str, Enum):
    RINGING = "ringing"
    ACTIVE = "active"
    HOLD = "hold"
    ENDED = "ended"


class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    WRAP_UP = "wrap-up"
    OFFLINE = "offline"


# ============================================
# Pydantic Models (API Request/Response)
# ============================================

class CallModeRequest(BaseModel):
    mode: CallMode
    agent: Optional[str] = None


class TransferRequest(BaseModel):
    target: str
    type: str = "blind"  # blind or attended


class AgentStatusRequest(BaseModel):
    status: AgentStatus


class CallInfo(BaseModel):
    call_id: str
    mode: str
    status: str
    caller_id: Optional[str] = None
    agent_id: Optional[str] = None
    started_at: Optional[str] = None
    channel_uuid: Optional[str] = None


class AgentInfo(BaseModel):
    agent_id: str
    name: str
    status: AgentStatus
    current_call: Optional[str] = None
    extension: Optional[str] = None


class ModeChangeResponse(BaseModel):
    call_id: str
    old_mode: str
    new_mode: str
    agent: Optional[str] = None


class TransferResponse(BaseModel):
    call_id: str
    transferred_to: str
    status: str


class RasaMessage(BaseModel):
    sender: str
    message: str


class DifyRequest(BaseModel):
    query: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None


# ============================================
# Dataclasses (Internal State)
# ============================================

@dataclass
class Call:
    call_id: str
    mode: CallMode = CallMode.AI
    status: CallStatus = CallStatus.ACTIVE
    caller_id: Optional[str] = None
    agent_id: Optional[str] = None
    channel_uuid: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "call_id": self.call_id,
            "mode": self.mode.value if isinstance(self.mode, CallMode) else self.mode,
            "status": self.status.value if isinstance(self.status, CallStatus) else self.status,
            "caller_id": self.caller_id,
            "agent_id": self.agent_id,
            "channel_uuid": self.channel_uuid,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


@dataclass
class Agent:
    agent_id: str
    name: str
    status: AgentStatus = AgentStatus.OFFLINE
    current_call: Optional[str] = None
    extension: Optional[str] = None
    sip_uri: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value if isinstance(self.status, AgentStatus) else self.status,
            "current_call": self.current_call,
            "extension": self.extension,
        }


@dataclass
class CallContext:
    """WebSocket session context"""
    call_id: str = ""
    call_uuid: str = ""
    sender_id: str = ""
    lang: str = "ja-JP"
    mode: CallMode = CallMode.AI
