"""
Voice Gateway - WebSocket Handler
音声ストリーム処理（FreeSWITCH ESL 連携）
"""
import os
import json
import base64
import asyncio
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv

from .models import CallContext, CallMode
from .state import state_manager
from .mode_manager import mode_manager
from .transcribe_service import TranscribeSession
from .polly_service import PollySession
from .rasa_client import rasa_client

load_dotenv()

POLLY_SAMPLE_RATE = int(os.getenv("POLLY_SAMPLE_RATE", "8000"))


class WebSocketHandler:
    """
    WebSocket 音声ストリーム処理
    """
    
    def __init__(self):
        self.transcribe = TranscribeSession()
        self.polly = PollySession()
        self._tts_lock = asyncio.Lock()
    
    async def handle_connection(self, ws: WebSocket, call_id: Optional[str] = None):
        """
        WebSocket 接続を処理
        
        Args:
            ws: WebSocket 接続
            call_id: 通話ID（URLパラメータから）
        """
        await ws.accept()
        
        # コンテキスト初期化
        ctx = CallContext(
            call_id=call_id or f"call-{id(ws)}",
            sender_id=f"caller-{id(ws)}",
            mode=CallMode.AI
        )
        
        # 状態に登録
        call = await state_manager.create_call(
            call_id=ctx.call_id,
            channel_uuid=ctx.call_uuid
        )
        state_manager.register_ws(ctx.call_id, ws)
        
        # Transcribe セッション開始
        async def on_final_text(text: str):
            """音声認識結果を処理"""
            # 現在のモードを確認
            current_call = await state_manager.get_call(ctx.call_id)
            if current_call and current_call.mode != CallMode.AI:
                # AI モードでない場合は処理しない
                return
            
            # Rasa に問い合わせ
            reply = await rasa_client.get_response_text(ctx.sender_id, text)
            
            # TTS で応答
            await self._send_tts_response(ws, reply)
        
        async def on_transcribe_error(e: Exception):
            """Transcribe エラー処理"""
            print(f"Transcribe error: {e}")
            fallback = "すみません、音声が認識できませんでした。"
            await self._send_tts_response(ws, fallback)
        
        await self.transcribe.start(on_final_text, on_transcribe_error)
        
        try:
            # 最初のメッセージ（メタデータの可能性）
            first = await ws.receive()
            await self._process_message(first, ctx)
            
            # メインループ
            while True:
                msg = await ws.receive()
                await self._process_message(msg, ctx)
        
        except WebSocketDisconnect:
            print(f"WebSocket disconnected: {ctx.call_id}")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            # クリーンアップ
            await self.transcribe.stop()
            state_manager.unregister_ws(ctx.call_id)
            await state_manager.end_call(ctx.call_id)
    
    async def _process_message(self, msg: dict, ctx: CallContext):
        """
        WebSocket メッセージを処理
        
        Args:
            msg: 受信メッセージ
            ctx: 通話コンテキスト
        """
        if msg.get("text"):
            # テキストメッセージ（メタデータ/コントロール）
            try:
                data = json.loads(msg["text"])
                await self._handle_control_message(data, ctx)
            except json.JSONDecodeError:
                pass
        
        elif msg.get("bytes") is not None:
            # バイナリメッセージ（音声データ）
            await self.transcribe.feed_audio(msg["bytes"])
    
    async def _handle_control_message(self, data: dict, ctx: CallContext):
        """
        コントロールメッセージを処理
        
        Args:
            data: JSON データ
            ctx: 通話コンテキスト
        """
        msg_type = data.get("type", "")
        
        if msg_type == "init" or "call_uuid" in data:
            # 初期化メッセージ
            ctx.call_uuid = data.get("call_uuid", ctx.call_uuid)
            ctx.call_id = data.get("call_id", ctx.call_id)
            ctx.lang = data.get("lang", ctx.lang)
            
            # 状態を更新
            call = await state_manager.get_call(ctx.call_id)
            if call:
                call.channel_uuid = ctx.call_uuid
        
        elif msg_type == "mode_change":
            # モード変更リクエスト
            new_mode = data.get("mode", "ai")
            agent_id = data.get("agent")
            
            if new_mode == "ai":
                ctx.mode = CallMode.AI
                await mode_manager.set_mode(ctx.call_id, CallMode.AI)
            elif new_mode == "human":
                ctx.mode = CallMode.HUMAN
                await mode_manager.set_mode(ctx.call_id, CallMode.HUMAN, agent_id)
        
        elif msg_type == "end":
            # 通話終了
            await state_manager.end_call(ctx.call_id)
    
    async def _send_tts_response(self, ws: WebSocket, text: str):
        """
        TTS 応答を送信
        
        Args:
            ws: WebSocket 接続
            text: 応答テキスト
        """
        async with self._tts_lock:
            try:
                # Polly で音声合成
                pcm_data = await self.polly.synthesize(text)
                
                # WebSocket で送信
                await self._send_audio_stream(ws, pcm_data)
            
            except Exception as e:
                print(f"TTS error: {e}")
                # フォールバック
                try:
                    fallback_pcm = await self.polly.synthesize(
                        "すみません、担当者におつなぎします。",
                        use_cache=True
                    )
                    await self._send_audio_stream(ws, fallback_pcm)
                except Exception:
                    pass
    
    async def _send_audio_stream(self, ws: WebSocket, pcm_data: bytes):
        """
        音声ストリームを送信
        
        Args:
            ws: WebSocket 接続
            pcm_data: PCM 音声データ
        """
        b64_data = base64.b64encode(pcm_data).decode("ascii")
        
        msg = {
            "type": "streamAudio",
            "data": {
                "audioDataType": "raw",
                "sampleRate": POLLY_SAMPLE_RATE,
                "audioData": b64_data
            }
        }
        
        await ws.send_text(json.dumps(msg, ensure_ascii=False))


# ハンドラファクトリ
def create_handler() -> WebSocketHandler:
    """新しい WebSocket ハンドラを作成"""
    return WebSocketHandler()
