"""
Voice Gateway - FreeSWITCH ESL Client
FreeSWITCH Event Socket Layer との連携
"""
import os
import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable
from dotenv import load_dotenv

load_dotenv()

FREESWITCH_HOST = os.getenv("FREESWITCH_HOST", "freeswitch")
FREESWITCH_PORT = int(os.getenv("FREESWITCH_PORT", "8021"))
FREESWITCH_PASSWORD = os.getenv("FREESWITCH_PASSWORD", "ClueCon")


class ESLClient:
    """
    FreeSWITCH ESL (Event Socket Layer) クライアント
    通話制御・転送・イベント受信
    """
    
    def __init__(
        self,
        host: str = FREESWITCH_HOST,
        port: int = FREESWITCH_PORT,
        password: str = FREESWITCH_PASSWORD
    ):
        self.host = host
        self.port = port
        self.password = password
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._event_handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
    
    async def connect(self) -> bool:
        """
        FreeSWITCH に接続
        
        Returns:
            接続成功ならTrue
        """
        try:
            self._reader, self._writer = await asyncio.open_connection(
                self.host, self.port
            )
            
            # 認証待ち
            response = await self._read_response()
            if "Content-Type: auth/request" not in response:
                return False
            
            # 認証
            await self._send_command(f"auth {self.password}")
            response = await self._read_response()
            
            if "+OK" in response or "Reply-Text: +OK" in response:
                self._connected = True
                return True
            
            return False
            
        except Exception as e:
            print(f"ESL connect error: {e}")
            return False
    
    async def disconnect(self):
        """接続を切断"""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._connected = False
        self._reader = None
        self._writer = None
    
    @property
    def connected(self) -> bool:
        """接続状態"""
        return self._connected
    
    async def _send_command(self, command: str):
        """コマンドを送信"""
        if not self._writer:
            raise ConnectionError("Not connected to FreeSWITCH")
        
        self._writer.write(f"{command}\n\n".encode())
        await self._writer.drain()
    
    async def _read_response(self) -> str:
        """応答を読み取り"""
        if not self._reader:
            raise ConnectionError("Not connected to FreeSWITCH")
        
        response_lines = []
        content_length = 0
        
        # ヘッダー読み取り
        while True:
            line = await self._reader.readline()
            line_str = line.decode().strip()
            
            if not line_str:
                break
            
            response_lines.append(line_str)
            
            if line_str.startswith("Content-Length:"):
                content_length = int(line_str.split(":")[1].strip())
        
        # ボディ読み取り
        if content_length > 0:
            body = await self._reader.read(content_length)
            response_lines.append(body.decode())
        
        return "\n".join(response_lines)
    
    async def api(self, command: str) -> str:
        """
        API コマンドを実行
        
        Args:
            command: FreeSWITCH API コマンド
        
        Returns:
            実行結果
        """
        if not self._connected:
            if not await self.connect():
                return "ERROR: Not connected"
        
        try:
            await self._send_command(f"api {command}")
            return await self._read_response()
        except Exception as e:
            self._connected = False
            return f"ERROR: {e}"
    
    async def bgapi(self, command: str) -> str:
        """
        バックグラウンド API コマンドを実行
        
        Args:
            command: FreeSWITCH API コマンド
        
        Returns:
            Job-UUID
        """
        if not self._connected:
            if not await self.connect():
                return "ERROR: Not connected"
        
        try:
            await self._send_command(f"bgapi {command}")
            response = await self._read_response()
            # Job-UUID を抽出
            for line in response.split("\n"):
                if "Job-UUID:" in line:
                    return line.split(":")[1].strip()
            return response
        except Exception as e:
            self._connected = False
            return f"ERROR: {e}"
    
    # ============================================
    # 通話制御コマンド
    # ============================================
    
    async def transfer(
        self,
        channel_uuid: str,
        destination: str,
        dialplan: str = "XML",
        context: str = "internal"
    ) -> str:
        """
        通話を転送
        
        Args:
            channel_uuid: チャネルUUID
            destination: 転送先（坐席ID等）
            dialplan: ダイアルプラン
            context: コンテキスト
        
        Returns:
            実行結果
        """
        cmd = f"uuid_transfer {channel_uuid} {destination} {dialplan} {context}"
        return await self.api(cmd)
    
    async def bridge(
        self,
        channel_uuid: str,
        destination: str
    ) -> str:
        """
        通話をブリッジ
        
        Args:
            channel_uuid: チャネルUUID
            destination: 接続先
        
        Returns:
            実行結果
        """
        cmd = f"uuid_bridge {channel_uuid} {destination}"
        return await self.api(cmd)
    
    async def hangup(
        self,
        channel_uuid: str,
        cause: str = "NORMAL_CLEARING"
    ) -> str:
        """
        通話を切断
        
        Args:
            channel_uuid: チャネルUUID
            cause: 切断理由
        
        Returns:
            実行結果
        """
        cmd = f"uuid_kill {channel_uuid} {cause}"
        return await self.api(cmd)
    
    async def hold(self, channel_uuid: str) -> str:
        """
        通話を保留
        
        Args:
            channel_uuid: チャネルUUID
        
        Returns:
            実行結果
        """
        cmd = f"uuid_hold {channel_uuid}"
        return await self.api(cmd)
    
    async def unhold(self, channel_uuid: str) -> str:
        """
        保留を解除
        
        Args:
            channel_uuid: チャネルUUID
        
        Returns:
            実行結果
        """
        cmd = f"uuid_hold off {channel_uuid}"
        return await self.api(cmd)
    
    async def playback(
        self,
        channel_uuid: str,
        file_path: str
    ) -> str:
        """
        音声ファイルを再生
        
        Args:
            channel_uuid: チャネルUUID
            file_path: 音声ファイルパス
        
        Returns:
            実行結果
        """
        cmd = f"uuid_broadcast {channel_uuid} {file_path}"
        return await self.api(cmd)
    
    async def set_variable(
        self,
        channel_uuid: str,
        variable: str,
        value: str
    ) -> str:
        """
        チャネル変数を設定
        
        Args:
            channel_uuid: チャネルUUID
            variable: 変数名
            value: 値
        
        Returns:
            実行結果
        """
        cmd = f"uuid_setvar {channel_uuid} {variable} {value}"
        return await self.api(cmd)
    
    async def get_variable(
        self,
        channel_uuid: str,
        variable: str
    ) -> str:
        """
        チャネル変数を取得
        
        Args:
            channel_uuid: チャネルUUID
            variable: 変数名
        
        Returns:
            変数値
        """
        cmd = f"uuid_getvar {channel_uuid} {variable}"
        result = await self.api(cmd)
        # 結果をパース
        for line in result.split("\n"):
            if not line.startswith("Content") and not line.startswith("Reply"):
                return line.strip()
        return ""
    
    # ============================================
    # チャネル情報
    # ============================================
    
    async def get_channels(self) -> str:
        """
        アクティブチャネル一覧を取得
        
        Returns:
            チャネル一覧
        """
        return await self.api("show channels")
    
    async def get_calls(self) -> str:
        """
        アクティブ通話一覧を取得
        
        Returns:
            通話一覧
        """
        return await self.api("show calls")
    
    async def channel_exists(self, channel_uuid: str) -> bool:
        """
        チャネルが存在するか確認
        
        Args:
            channel_uuid: チャネルUUID
        
        Returns:
            存在すればTrue
        """
        result = await self.api(f"uuid_exists {channel_uuid}")
        return "true" in result.lower()
    
    # ============================================
    # 坐席関連
    # ============================================
    
    async def originate_to_agent(
        self,
        agent_uri: str,
        caller_id_name: str = "AI Assistant",
        caller_id_number: str = "0000"
    ) -> str:
        """
        坐席に発信
        
        Args:
            agent_uri: 坐席 SIP URI (例: user/agent-001)
            caller_id_name: 発信者名
            caller_id_number: 発信者番号
        
        Returns:
            実行結果
        """
        cmd = (
            f"originate {{{{"
            f"origination_caller_id_name={caller_id_name},"
            f"origination_caller_id_number={caller_id_number}"
            f"}}}}{agent_uri} &park()"
        )
        return await self.bgapi(cmd)
    
    async def transfer_to_agent(
        self,
        channel_uuid: str,
        agent_id: str,
        domain: str = "freeswitch"
    ) -> str:
        """
        坐席に転送（内部プロファイル経由）
        
        Args:
            channel_uuid: チャネルUUID
            agent_id: 坐席ID
            domain: ドメイン
        
        Returns:
            実行結果
        """
        destination = f"user/{agent_id}@{domain}"
        return await self.transfer(channel_uuid, destination, "XML", "internal")
    
    # ============================================
    # イベント購読
    # ============================================
    
    async def subscribe_events(self, events: str = "all") -> str:
        """
        イベントを購読
        
        Args:
            events: 購読するイベント（"all" または "CHANNEL_CREATE CHANNEL_HANGUP" 等）
        
        Returns:
            購読結果
        """
        await self._send_command(f"event plain {events}")
        return await self._read_response()
    
    async def listen_events(
        self,
        handler: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        """
        イベントをリッスン（非同期ループ）
        
        Args:
            handler: イベントハンドラ
        """
        if not self._connected:
            await self.connect()
        
        await self.subscribe_events()
        
        while self._connected:
            try:
                response = await self._read_response()
                event = self._parse_event(response)
                if event:
                    await handler(event)
            except Exception as e:
                print(f"Event listen error: {e}")
                break
    
    def _parse_event(self, response: str) -> Optional[Dict[str, Any]]:
        """イベントをパース"""
        if not response:
            return None
        
        event = {}
        for line in response.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                event[key.strip()] = value.strip()
        
        return event if event else None


# デフォルトインスタンス
esl_client = ESLClient()
