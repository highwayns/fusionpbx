"""
Voice Gateway - Dify Client
Dify LLM + 知識庫 (RAG) との連携
"""
import os
from typing import Optional, Dict, Any, AsyncIterator
import httpx
from dotenv import load_dotenv

load_dotenv()

DIFY_API_URL = os.getenv("DIFY_API_URL", "http://dify-api:5001/v1")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
DIFY_TIMEOUT = float(os.getenv("DIFY_TIMEOUT", "30.0"))


class DifyClient:
    """
    Dify API クライアント
    LLM + RAG 検索による応答生成
    """
    
    def __init__(
        self,
        api_url: str = DIFY_API_URL,
        api_key: str = DIFY_API_KEY,
        timeout: float = DIFY_TIMEOUT
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        response_mode: str = "blocking"
    ) -> Dict[str, Any]:
        """
        Dify Chat API を呼び出し
        
        Args:
            query: ユーザークエリ
            user: ユーザーID
            conversation_id: 会話ID（継続する場合）
            inputs: 追加入力変数
            response_mode: "blocking" or "streaming"
        
        Returns:
            Dify からの応答
        """
        url = f"{self.api_url}/chat-messages"
        
        payload = {
            "query": query,
            "user": user,
            "response_mode": response_mode,
            "inputs": inputs or {}
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            return {"error": "timeout", "answer": "申し訳ございません。応答に時間がかかっております。"}
        except Exception as e:
            print(f"Dify chat error: {e}")
            return {"error": str(e), "answer": "システムエラーが発生しました。"}
    
    async def run_workflow(
        self,
        inputs: Dict[str, Any],
        user: str,
        response_mode: str = "blocking"
    ) -> Dict[str, Any]:
        """
        Dify Workflow を実行
        
        Args:
            inputs: ワークフロー入力
            user: ユーザーID
            response_mode: "blocking" or "streaming"
        
        Returns:
            ワークフロー実行結果
        """
        url = f"{self.api_url}/workflows/run"
        
        payload = {
            "inputs": inputs,
            "user": user,
            "response_mode": response_mode
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            return {"error": "timeout"}
        except Exception as e:
            print(f"Dify workflow error: {e}")
            return {"error": str(e)}
    
    async def get_response_text(
        self,
        query: str,
        user: str,
        conversation_id: Optional[str] = None,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Dify からテキスト応答のみを取得（簡易版）
        
        Args:
            query: ユーザークエリ
            user: ユーザーID
            conversation_id: 会話ID
            intent: Rasa から取得した意図
            entities: Rasa から取得したエンティティ
        
        Returns:
            応答テキスト
        """
        inputs = {}
        if intent:
            inputs["intent"] = intent
        if entities:
            inputs["entities"] = entities
        
        result = await self.chat(
            query=query,
            user=user,
            conversation_id=conversation_id,
            inputs=inputs
        )
        
        return result.get("answer", "申し訳ございません。もう一度お願いします。")
    
    async def query_knowledge(
        self,
        query: str,
        user: str,
        dataset_id: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        知識庫を検索（RAG）
        
        Args:
            query: 検索クエリ
            user: ユーザーID
            dataset_id: データセットID
            top_k: 取得件数
        
        Returns:
            検索結果
        """
        # Dify の retrieval API を使用
        url = f"{self.api_url}/retrieval"
        
        payload = {
            "query": query,
            "user": user,
            "top_k": top_k
        }
        
        if dataset_id:
            payload["dataset_id"] = dataset_id
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Dify knowledge query error: {e}")
            return {"records": []}
    
    async def get_conversations(
        self,
        user: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        会話履歴を取得
        
        Args:
            user: ユーザーID
            limit: 取得件数
        
        Returns:
            会話リスト
        """
        url = f"{self.api_url}/conversations"
        params = {
            "user": user,
            "limit": limit
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Dify conversations error: {e}")
            return {"data": []}
    
    async def get_messages(
        self,
        conversation_id: str,
        user: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        会話内メッセージを取得
        
        Args:
            conversation_id: 会話ID
            user: ユーザーID
            limit: 取得件数
        
        Returns:
            メッセージリスト
        """
        url = f"{self.api_url}/messages"
        params = {
            "conversation_id": conversation_id,
            "user": user,
            "limit": limit
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Dify messages error: {e}")
            return {"data": []}
    
    async def health_check(self) -> bool:
        """
        Dify サーバーのヘルスチェック
        
        Returns:
            正常ならTrue
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # シンプルなパラメータAPIを呼び出し
                response = await client.get(
                    f"{self.api_url}/parameters",
                    headers=self._headers
                )
                return response.status_code in [200, 401]  # 401でもサーバーは生きている
        except Exception:
            return False


# デフォルトインスタンス
dify_client = DifyClient()
