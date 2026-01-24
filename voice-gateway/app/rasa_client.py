"""
Voice Gateway - Rasa Client
Rasa NLU/対話管理との連携
"""
import os
from typing import Optional, List, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

RASA_URL = os.getenv("RASA_URL", "http://rasa:5005")
RASA_REST_ENDPOINT = os.getenv("RASA_REST_ENDPOINT", f"{RASA_URL}/webhooks/rest/webhook")
RASA_TIMEOUT = float(os.getenv("RASA_TIMEOUT", "20.0"))


class RasaClient:
    """
    Rasa REST API クライアント
    テキストベースの NLU/対話管理
    """
    
    def __init__(
        self,
        base_url: str = RASA_URL,
        webhook_url: str = RASA_REST_ENDPOINT,
        timeout: float = RASA_TIMEOUT
    ):
        self.base_url = base_url
        self.webhook_url = webhook_url
        self.timeout = timeout
    
    async def send_message(
        self,
        sender: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rasa にメッセージを送信し、応答を取得
        
        Args:
            sender: 送信者ID（通話ID等）
            message: ユーザーメッセージ
            metadata: 追加メタデータ
        
        Returns:
            Rasa からの応答リスト [{"text": "...", "buttons": [...], ...}]
        """
        payload = {
            "sender": sender,
            "message": message,
        }
        if metadata:
            payload["metadata"] = metadata
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            return [{"text": "申し訳ございません。応答に時間がかかっております。"}]
        except Exception as e:
            print(f"Rasa error: {e}")
            return [{"text": "すみません、担当者におつなぎします。"}]
    
    async def get_response_text(
        self,
        sender: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Rasa からテキスト応答のみを取得
        
        Args:
            sender: 送信者ID
            message: ユーザーメッセージ
            metadata: 追加メタデータ
        
        Returns:
            結合されたテキスト応答
        """
        responses = await self.send_message(sender, message, metadata)
        
        texts = []
        for item in responses:
            if isinstance(item, dict) and item.get("text"):
                texts.append(item["text"])
        
        return "\n".join(texts) if texts else "すみません、もう一度お願いします。"
    
    async def get_tracker(self, sender: str) -> Optional[Dict[str, Any]]:
        """
        Rasa トラッカー（会話状態）を取得
        
        Args:
            sender: 送信者ID
        
        Returns:
            トラッカー情報
        """
        url = f"{self.base_url}/conversations/{sender}/tracker"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params={"include_events": "ALL"})
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Rasa tracker error: {e}")
            return None
    
    async def get_tracker_events(self, sender: str) -> List[Dict[str, Any]]:
        """
        会話イベント履歴を取得
        
        Args:
            sender: 送信者ID
        
        Returns:
            イベントリスト
        """
        tracker = await self.get_tracker(sender)
        if tracker:
            return tracker.get("events", [])
        return []
    
    async def get_story(self, sender: str) -> Optional[str]:
        """
        会話ストーリーを取得
        
        Args:
            sender: 送信者ID
        
        Returns:
            ストーリー文字列
        """
        url = f"{self.base_url}/conversations/{sender}/story"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"Rasa story error: {e}")
            return None
    
    async def parse_message(self, message: str) -> Optional[Dict[str, Any]]:
        """
        メッセージを解析（NLUのみ、対話なし）
        
        Args:
            message: 解析するメッセージ
        
        Returns:
            NLU結果（intent, entities等）
        """
        url = f"{self.base_url}/model/parse"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json={"text": message})
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Rasa parse error: {e}")
            return None
    
    async def trigger_intent(
        self,
        sender: str,
        intent: str,
        entities: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        意図を直接トリガー
        
        Args:
            sender: 送信者ID
            intent: トリガーする意図名
            entities: エンティティリスト
        
        Returns:
            応答リスト
        """
        url = f"{self.base_url}/conversations/{sender}/trigger_intent"
        payload = {
            "name": intent,
        }
        if entities:
            payload["entities"] = entities
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("messages", [])
        except Exception as e:
            print(f"Rasa trigger error: {e}")
            return []
    
    async def health_check(self) -> bool:
        """
        Rasa サーバーのヘルスチェック
        
        Returns:
            正常ならTrue
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
                return response.status_code == 200
        except Exception:
            return False


# デフォルトインスタンス
rasa_client = RasaClient()
