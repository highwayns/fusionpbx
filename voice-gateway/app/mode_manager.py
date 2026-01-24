"""
Voice Gateway - Mode Manager
AI/Human モード切替管理
"""
import os
import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable
from dotenv import load_dotenv

from .models import CallMode, CallStatus, AgentStatus, Call, Agent
from .state import state_manager
from .esl_client import esl_client

load_dotenv()

FREESWITCH_DOMAIN = os.getenv("FREESWITCH_DOMAIN", "freeswitch")


class ModeManager:
    """
    通話モード管理
    AI自動応答 ⇄ 有人応答 の切替を制御
    """
    
    def __init__(self):
        self._mode_change_handlers: list = []
    
    def on_mode_change(
        self,
        handler: Callable[[str, CallMode, CallMode, Optional[str]], Awaitable[None]]
    ):
        """
        モード変更ハンドラを登録
        
        Args:
            handler: async (call_id, old_mode, new_mode, agent_id) -> None
        """
        self._mode_change_handlers.append(handler)
    
    async def _emit_mode_change(
        self,
        call_id: str,
        old_mode: CallMode,
        new_mode: CallMode,
        agent_id: Optional[str] = None
    ):
        """モード変更を通知"""
        for handler in self._mode_change_handlers:
            try:
                await handler(call_id, old_mode, new_mode, agent_id)
            except Exception as e:
                print(f"Mode change handler error: {e}")
    
    async def get_mode(self, call_id: str) -> Optional[CallMode]:
        """
        通話モードを取得
        
        Args:
            call_id: 通話ID
        
        Returns:
            現在のモード
        """
        call = await state_manager.get_call(call_id)
        if call:
            return call.mode
        return None
    
    async def set_mode(
        self,
        call_id: str,
        mode: CallMode,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        通話モードを設定
        
        Args:
            call_id: 通話ID
            mode: 新しいモード
            agent_id: 坐席ID（transfer モードの場合）
        
        Returns:
            結果 {"success": bool, "old_mode": str, "new_mode": str, ...}
        """
        call = await state_manager.get_call(call_id)
        if not call:
            return {"success": False, "error": "Call not found"}
        
        old_mode = call.mode
        
        # すでに同じモードの場合
        if old_mode == mode and mode != CallMode.TRANSFER:
            return {
                "success": True,
                "call_id": call_id,
                "old_mode": old_mode.value,
                "new_mode": mode.value,
                "message": "Mode unchanged"
            }
        
        # モード別処理
        if mode == CallMode.AI:
            result = await self._switch_to_ai(call)
        elif mode == CallMode.HUMAN:
            result = await self._switch_to_human(call, agent_id)
        elif mode == CallMode.TRANSFER:
            if not agent_id:
                return {"success": False, "error": "Agent ID required for transfer"}
            result = await self._transfer_to_agent(call, agent_id)
        else:
            return {"success": False, "error": f"Unknown mode: {mode}"}
        
        if result.get("success"):
            # 状態を更新
            await state_manager.update_call_mode(call_id, mode, agent_id)
            
            # ハンドラを呼び出し
            await self._emit_mode_change(call_id, old_mode, mode, agent_id)
        
        result["old_mode"] = old_mode.value
        return result
    
    async def _switch_to_ai(self, call: Call) -> Dict[str, Any]:
        """
        AIモードに切替
        
        Args:
            call: 通話オブジェクト
        
        Returns:
            結果
        """
        # 坐席を解放
        if call.agent_id:
            agent = await state_manager.get_agent(call.agent_id)
            if agent:
                await state_manager.update_agent_status(
                    call.agent_id,
                    AgentStatus.AVAILABLE
                )
        
        # FreeSWITCH に転送指示（Voice Gateway の ESL 処理に戻す）
        if call.channel_uuid:
            try:
                # Voice Gateway の処理に戻すための dialplan 呼び出し
                # 実際の実装では、カスタム dialplan を用意
                result = await esl_client.set_variable(
                    call.channel_uuid,
                    "call_mode",
                    "ai"
                )
            except Exception as e:
                print(f"ESL error (switch to AI): {e}")
        
        return {
            "success": True,
            "call_id": call.call_id,
            "new_mode": CallMode.AI.value,
            "message": "Switched to AI mode"
        }
    
    async def _switch_to_human(
        self,
        call: Call,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        有人モードに切替（空き坐席自動割当）
        
        Args:
            call: 通話オブジェクト
            agent_id: 指定坐席ID（None の場合は自動割当）
        
        Returns:
            結果
        """
        # 坐席を取得または自動割当
        if agent_id:
            agent = await state_manager.get_agent(agent_id)
            if not agent:
                return {"success": False, "error": f"Agent {agent_id} not found"}
            if agent.status != AgentStatus.AVAILABLE:
                return {"success": False, "error": f"Agent {agent_id} is not available"}
        else:
            agent_id = await state_manager.get_available_agent()
            if not agent_id:
                return {"success": False, "error": "No available agents"}
            agent = await state_manager.get_agent(agent_id)
        
        # 転送を実行
        return await self._transfer_to_agent(call, agent_id)
    
    async def _transfer_to_agent(
        self,
        call: Call,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        特定坐席に転送
        
        Args:
            call: 通話オブジェクト
            agent_id: 坐席ID
        
        Returns:
            結果
        """
        agent = await state_manager.get_agent(agent_id)
        if not agent:
            return {"success": False, "error": f"Agent {agent_id} not found"}
        
        if agent.status not in [AgentStatus.AVAILABLE, AgentStatus.WRAP_UP]:
            return {"success": False, "error": f"Agent {agent_id} is not available"}
        
        # FreeSWITCH で転送
        if call.channel_uuid:
            try:
                result = await esl_client.transfer_to_agent(
                    call.channel_uuid,
                    agent_id,
                    FREESWITCH_DOMAIN
                )
                
                if "ERROR" in result:
                    return {"success": False, "error": result}
                
            except Exception as e:
                print(f"ESL transfer error: {e}")
                return {"success": False, "error": str(e)}
        
        # 坐席状態を更新
        await state_manager.update_agent_status(agent_id, AgentStatus.BUSY)
        
        return {
            "success": True,
            "call_id": call.call_id,
            "new_mode": CallMode.TRANSFER.value,
            "agent_id": agent_id,
            "agent_name": agent.name,
            "message": f"Transferred to {agent.name}"
        }
    
    async def transfer(
        self,
        call_id: str,
        target_agent: str,
        transfer_type: str = "blind"
    ) -> Dict[str, Any]:
        """
        転送を実行
        
        Args:
            call_id: 通話ID
            target_agent: 転送先坐席ID
            transfer_type: "blind" or "attended"
        
        Returns:
            結果
        """
        call = await state_manager.get_call(call_id)
        if not call:
            return {"success": False, "error": "Call not found"}
        
        agent = await state_manager.get_agent(target_agent)
        if not agent:
            return {"success": False, "error": f"Agent {target_agent} not found"}
        
        if agent.status != AgentStatus.AVAILABLE:
            return {"success": False, "error": f"Agent {target_agent} is not available"}
        
        if transfer_type == "blind":
            # ブラインド転送（即時転送）
            return await self.set_mode(call_id, CallMode.TRANSFER, target_agent)
        else:
            # アテンデッド転送（確認後転送）
            # TODO: 実装
            return {"success": False, "error": "Attended transfer not implemented"}
    
    async def return_to_ai(self, call_id: str) -> Dict[str, Any]:
        """
        AIモードに戻す（坐席から呼び出し）
        
        Args:
            call_id: 通話ID
        
        Returns:
            結果
        """
        return await self.set_mode(call_id, CallMode.AI)


# デフォルトインスタンス
mode_manager = ModeManager()
