"""
Voice Gateway - State Management
通話・坐席の状態管理
"""
import asyncio
from datetime import datetime
from typing import Dict, Optional, List, Callable, Awaitable
from .models import Call, Agent, CallMode, CallStatus, AgentStatus

# Type for event callbacks
EventCallback = Callable[[str, dict], Awaitable[None]]


class StateManager:
    """
    通話と坐席の状態を管理するシングルトンクラス
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._calls: Dict[str, Call] = {}
        self._agents: Dict[str, Agent] = {}
        self._ws_connections: Dict[str, "WebSocket"] = {}  # call_id -> websocket
        self._event_listeners: List[EventCallback] = []
        self._lock = asyncio.Lock()
        self._initialized = True
        
        # デフォルト坐席を登録
        self._init_default_agents()
    
    def _init_default_agents(self):
        """デフォルト坐席の初期化"""
        default_agents = [
            Agent(
                agent_id="agent-001",
                name="山田太郎",
                status=AgentStatus.AVAILABLE,
                extension="1001",
                sip_uri="sip:agent-001@freeswitch"
            ),
            Agent(
                agent_id="agent-002", 
                name="鈴木花子",
                status=AgentStatus.AVAILABLE,
                extension="1002",
                sip_uri="sip:agent-002@freeswitch"
            ),
            Agent(
                agent_id="agent-003",
                name="田中一郎",
                status=AgentStatus.OFFLINE,
                extension="1003",
                sip_uri="sip:agent-003@freeswitch"
            ),
        ]
        for agent in default_agents:
            self._agents[agent.agent_id] = agent
    
    # ============================================
    # Event System
    # ============================================
    
    def add_event_listener(self, callback: EventCallback):
        """イベントリスナーを追加"""
        self._event_listeners.append(callback)
    
    def remove_event_listener(self, callback: EventCallback):
        """イベントリスナーを削除"""
        if callback in self._event_listeners:
            self._event_listeners.remove(callback)
    
    async def _emit_event(self, event_type: str, data: dict):
        """イベントを発火"""
        for listener in self._event_listeners:
            try:
                await listener(event_type, data)
            except Exception as e:
                print(f"Event listener error: {e}")
    
    # ============================================
    # Call Management
    # ============================================
    
    async def create_call(
        self,
        call_id: str,
        caller_id: Optional[str] = None,
        channel_uuid: Optional[str] = None,
        mode: CallMode = CallMode.AI
    ) -> Call:
        """新規通話を作成"""
        async with self._lock:
            call = Call(
                call_id=call_id,
                caller_id=caller_id,
                channel_uuid=channel_uuid,
                mode=mode,
                status=CallStatus.ACTIVE,
                started_at=datetime.now()
            )
            self._calls[call_id] = call
        
        await self._emit_event("call_created", call.to_dict())
        return call
    
    async def get_call(self, call_id: str) -> Optional[Call]:
        """通話を取得"""
        return self._calls.get(call_id)
    
    async def get_all_calls(self) -> List[Call]:
        """全通話を取得"""
        return list(self._calls.values())
    
    async def update_call_mode(
        self,
        call_id: str,
        mode: CallMode,
        agent_id: Optional[str] = None
    ) -> Optional[Call]:
        """通話モードを更新"""
        async with self._lock:
            call = self._calls.get(call_id)
            if not call:
                return None
            
            old_mode = call.mode
            call.mode = mode
            
            # Human/Transfer モードの場合は坐席を割り当て
            if mode in [CallMode.HUMAN, CallMode.TRANSFER] and agent_id:
                call.agent_id = agent_id
                # 坐席のステータスも更新
                if agent_id in self._agents:
                    self._agents[agent_id].status = AgentStatus.BUSY
                    self._agents[agent_id].current_call = call_id
            
            # AI モードに戻す場合は坐席を解放
            elif mode == CallMode.AI and call.agent_id:
                old_agent_id = call.agent_id
                if old_agent_id in self._agents:
                    self._agents[old_agent_id].status = AgentStatus.AVAILABLE
                    self._agents[old_agent_id].current_call = None
                call.agent_id = None
        
        await self._emit_event("call_mode_changed", {
            "call_id": call_id,
            "old_mode": old_mode.value if isinstance(old_mode, CallMode) else old_mode,
            "new_mode": mode.value if isinstance(mode, CallMode) else mode,
            "agent_id": agent_id
        })
        
        return call
    
    async def end_call(self, call_id: str) -> Optional[Call]:
        """通話を終了"""
        async with self._lock:
            call = self._calls.get(call_id)
            if not call:
                return None
            
            call.status = CallStatus.ENDED
            
            # 坐席を解放
            if call.agent_id and call.agent_id in self._agents:
                self._agents[call.agent_id].status = AgentStatus.WRAP_UP
                self._agents[call.agent_id].current_call = None
        
        await self._emit_event("call_ended", call.to_dict())
        return call
    
    async def remove_call(self, call_id: str):
        """通話を削除"""
        async with self._lock:
            if call_id in self._calls:
                del self._calls[call_id]
            if call_id in self._ws_connections:
                del self._ws_connections[call_id]
    
    # ============================================
    # Agent Management
    # ============================================
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """坐席を取得"""
        return self._agents.get(agent_id)
    
    async def get_all_agents(self) -> Dict[str, Agent]:
        """全坐席を取得"""
        return self._agents.copy()
    
    async def get_available_agent(self) -> Optional[str]:
        """空き坐席を取得"""
        for agent_id, agent in self._agents.items():
            if agent.status == AgentStatus.AVAILABLE:
                return agent_id
        return None
    
    async def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus
    ) -> Optional[Agent]:
        """坐席ステータスを更新"""
        async with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                return None
            
            old_status = agent.status
            agent.status = status
            
            # オフラインになった場合、通話をAIに戻す
            if status == AgentStatus.OFFLINE and agent.current_call:
                call_id = agent.current_call
                if call_id in self._calls:
                    self._calls[call_id].mode = CallMode.AI
                    self._calls[call_id].agent_id = None
                agent.current_call = None
        
        await self._emit_event("agent_status_changed", {
            "agent_id": agent_id,
            "old_status": old_status.value if isinstance(old_status, AgentStatus) else old_status,
            "new_status": status.value if isinstance(status, AgentStatus) else status
        })
        
        return agent
    
    async def register_agent(self, agent: Agent) -> Agent:
        """坐席を登録"""
        async with self._lock:
            self._agents[agent.agent_id] = agent
        
        await self._emit_event("agent_registered", agent.to_dict())
        return agent
    
    # ============================================
    # WebSocket Connection Management
    # ============================================
    
    def register_ws(self, call_id: str, ws: "WebSocket"):
        """WebSocket接続を登録"""
        self._ws_connections[call_id] = ws
    
    def unregister_ws(self, call_id: str):
        """WebSocket接続を解除"""
        if call_id in self._ws_connections:
            del self._ws_connections[call_id]
    
    def get_ws(self, call_id: str) -> Optional["WebSocket"]:
        """WebSocket接続を取得"""
        return self._ws_connections.get(call_id)


# シングルトンインスタンス
state_manager = StateManager()
