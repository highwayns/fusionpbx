"""
Voice Gateway - Main Application
AI呼叫中心 Voice Gateway メインアプリケーション

機能:
- WebSocket 音声ストリーム処理
- Amazon Transcribe (STT)
- Amazon Polly (TTS)
- Rasa NLU 連携
- Dify LLM 連携
- Mode Manager (AI/Human 切替)
- FreeSWITCH ESL 連携
- REST API (Mindoo UI 向け)
"""
import os
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

from .models import (
    CallMode, CallStatus, AgentStatus,
    CallModeRequest, TransferRequest, AgentStatusRequest,
    CallInfo, AgentInfo, ModeChangeResponse, TransferResponse,
    RasaMessage, DifyRequest
)
from .state import state_manager
from .mode_manager import mode_manager
from .rasa_client import rasa_client
from .dify_client import dify_client
from .esl_client import esl_client
from .ws_handler import create_handler

load_dotenv()

# ============================================
# Application Lifecycle
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル"""
    # Startup
    print("Voice Gateway starting...")
    
    # ESL 接続（オプション）
    try:
        if await esl_client.connect():
            print("Connected to FreeSWITCH ESL")
    except Exception as e:
        print(f"FreeSWITCH ESL connection failed (non-fatal): {e}")
    
    yield
    
    # Shutdown
    print("Voice Gateway shutting down...")
    await esl_client.disconnect()


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="Voice Gateway",
    description="AI呼叫中心 Voice Gateway - STT/TTS + Rasa/Dify + Mode Manager",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Health Check
# ============================================

@app.get("/health", response_class=PlainTextResponse, tags=["Health"])
async def health():
    """ヘルスチェック"""
    return "OK"


@app.get("/health/detailed", tags=["Health"])
async def health_detailed():
    """詳細ヘルスチェック"""
    rasa_ok = await rasa_client.health_check()
    dify_ok = await dify_client.health_check()
    
    return {
        "status": "ok" if (rasa_ok or dify_ok) else "degraded",
        "services": {
            "rasa": "ok" if rasa_ok else "error",
            "dify": "ok" if dify_ok else "error",
            "freeswitch": "ok" if esl_client.connected else "disconnected"
        }
    }


# ============================================
# WebSocket Endpoints
# ============================================

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    """
    WebSocket 音声ストリーム処理（デフォルト）
    """
    handler = create_handler()
    await handler.handle_connection(ws)


@app.websocket("/ws/{call_id}")
async def ws_endpoint_with_call_id(ws: WebSocket, call_id: str):
    """
    WebSocket 音声ストリーム処理（通話ID指定）
    """
    handler = create_handler()
    await handler.handle_connection(ws, call_id)


# ============================================
# Call Management API
# ============================================

@app.post("/calls/{call_id}/init", tags=["Calls"])
async def init_call(
    call_id: str,
    caller_id: Optional[str] = None,
    channel_uuid: Optional[str] = None
):
    """
    通話初期化（FreeSWITCH Dialplan から呼び出し）
    """
    call = await state_manager.create_call(
        call_id=call_id,
        caller_id=caller_id,
        channel_uuid=channel_uuid,
        mode=CallMode.AI
    )
    return {"call_id": call_id, "mode": "ai", "status": "active"}


@app.get("/calls", tags=["Calls"])
async def list_calls():
    """通話一覧"""
    calls = await state_manager.get_all_calls()
    return {
        "calls": [call.to_dict() for call in calls],
        "total": len(calls)
    }


@app.get("/calls/{call_id}", tags=["Calls"])
async def get_call(call_id: str):
    """通話詳細"""
    call = await state_manager.get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call.to_dict()


@app.delete("/calls/{call_id}", tags=["Calls"])
async def end_call(call_id: str):
    """通話終了"""
    call = await state_manager.end_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return {"call_id": call_id, "status": "ended"}


# ============================================
# Mode Management API
# ============================================

@app.get("/calls/{call_id}/mode", tags=["Mode"])
async def get_call_mode(call_id: str):
    """通話モード取得"""
    mode = await mode_manager.get_mode(call_id)
    if mode is None:
        # デフォルトはAI
        return "ai"
    return mode.value


@app.put("/calls/{call_id}/mode", tags=["Mode"])
async def set_call_mode(call_id: str, request: CallModeRequest):
    """
    通話モード変更
    
    - mode: "ai" | "human" | "transfer"
    - agent: 坐席ID（transfer モードの場合必須）
    """
    result = await mode_manager.set_mode(
        call_id=call_id,
        mode=request.mode,
        agent_id=request.agent
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400 if "not found" not in result.get("error", "").lower() else 404,
            detail=result.get("error", "Failed to change mode")
        )
    
    return ModeChangeResponse(
        call_id=call_id,
        old_mode=result.get("old_mode", ""),
        new_mode=result.get("new_mode", request.mode.value),
        agent=result.get("agent_id")
    )


@app.post("/calls/{call_id}/transfer", tags=["Mode"])
async def transfer_call(call_id: str, request: TransferRequest):
    """
    通話転送
    
    - target: 転送先坐席ID
    - type: "blind" | "attended"
    """
    result = await mode_manager.transfer(
        call_id=call_id,
        target_agent=request.target,
        transfer_type=request.type
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400 if "not found" not in result.get("error", "").lower() else 404,
            detail=result.get("error", "Transfer failed")
        )
    
    return TransferResponse(
        call_id=call_id,
        transferred_to=request.target,
        status="transferred"
    )


# ============================================
# Agent Management API
# ============================================

@app.get("/agents", tags=["Agents"])
async def list_agents():
    """坐席一覧"""
    agents = await state_manager.get_all_agents()
    return {agent_id: agent.to_dict() for agent_id, agent in agents.items()}


@app.get("/agents/available", tags=["Agents"])
async def get_available_agent():
    """空き坐席取得"""
    agent_id = await state_manager.get_available_agent()
    return agent_id


@app.get("/agents/{agent_id}", tags=["Agents"])
async def get_agent(agent_id: str):
    """坐席詳細"""
    agent = await state_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()


@app.get("/agents/{agent_id}/status", tags=["Agents"])
async def get_agent_status(agent_id: str):
    """坐席状態取得"""
    agent = await state_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"agent_id": agent_id, "status": agent.status.value}


@app.put("/agents/{agent_id}/status", tags=["Agents"])
async def set_agent_status(agent_id: str, request: AgentStatusRequest):
    """坐席状態更新"""
    agent = await state_manager.update_agent_status(agent_id, request.status)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()


# ============================================
# Rasa Integration API
# ============================================

@app.post("/rasa/message", tags=["Rasa"])
async def send_rasa_message(request: RasaMessage):
    """Rasa にメッセージ送信"""
    responses = await rasa_client.send_message(request.sender, request.message)
    return {"responses": responses}


@app.get("/rasa/conversations/{sender_id}", tags=["Rasa"])
async def get_rasa_conversation(sender_id: str):
    """Rasa 会話履歴取得"""
    tracker = await rasa_client.get_tracker(sender_id)
    if not tracker:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return tracker


@app.get("/rasa/conversations/{sender_id}/story", tags=["Rasa"])
async def get_rasa_story(sender_id: str):
    """Rasa ストーリー取得"""
    story = await rasa_client.get_story(sender_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return PlainTextResponse(story)


@app.post("/rasa/parse", tags=["Rasa"])
async def parse_rasa_message(message: str = Query(...)):
    """Rasa NLU 解析（対話なし）"""
    result = await rasa_client.parse_message(message)
    if not result:
        raise HTTPException(status_code=500, detail="Parse failed")
    return result


# ============================================
# Dify Integration API
# ============================================

@app.post("/dify/chat", tags=["Dify"])
async def dify_chat(request: DifyRequest):
    """Dify Chat API"""
    result = await dify_client.chat(
        query=request.query,
        user=request.conversation_id or "default",
        conversation_id=request.conversation_id,
        inputs={
            "intent": request.intent,
            "entities": request.entities
        } if request.intent else None
    )
    return result


@app.post("/dify/workflow", tags=["Dify"])
async def dify_workflow(request: DifyRequest):
    """Dify Workflow 実行"""
    inputs = {
        "query": request.query,
    }
    if request.intent:
        inputs["intent"] = request.intent
    if request.entities:
        inputs["entities"] = request.entities
    
    result = await dify_client.run_workflow(
        inputs=inputs,
        user=request.conversation_id or "default"
    )
    return result


# ============================================
# FreeSWITCH ESL API
# ============================================

@app.post("/freeswitch/command", tags=["FreeSWITCH"])
async def freeswitch_command(command: str = Query(...)):
    """FreeSWITCH API コマンド実行"""
    if not esl_client.connected:
        if not await esl_client.connect():
            raise HTTPException(status_code=503, detail="FreeSWITCH not connected")
    
    result = await esl_client.api(command)
    return {"command": command, "result": result}


@app.get("/freeswitch/channels", tags=["FreeSWITCH"])
async def get_freeswitch_channels():
    """FreeSWITCH アクティブチャネル"""
    if not esl_client.connected:
        raise HTTPException(status_code=503, detail="FreeSWITCH not connected")
    
    result = await esl_client.get_channels()
    return PlainTextResponse(result)


@app.get("/freeswitch/calls", tags=["FreeSWITCH"])
async def get_freeswitch_calls():
    """FreeSWITCH アクティブ通話"""
    if not esl_client.connected:
        raise HTTPException(status_code=503, detail="FreeSWITCH not connected")
    
    result = await esl_client.get_calls()
    return PlainTextResponse(result)


# ============================================
# Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    
    uvicorn.run(app, host=host, port=port)
