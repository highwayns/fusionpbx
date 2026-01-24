"""
Voice Gateway - Amazon Polly Service
音声合成 (TTS) サービス
"""
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
POLLY_VOICE_ID = os.getenv("POLLY_VOICE_ID", "Takumi")
POLLY_SAMPLE_RATE = int(os.getenv("POLLY_SAMPLE_RATE", "8000"))
POLLY_ENGINE = os.getenv("POLLY_ENGINE", "neural")  # standard or neural

# スレッドプール（同期 Polly API を非同期で実行）
_executor = ThreadPoolExecutor(max_workers=4)


class PollyService:
    """
    Amazon Polly TTS サービス
    """
    
    def __init__(
        self,
        region: str = AWS_REGION,
        voice_id: str = POLLY_VOICE_ID,
        sample_rate: int = POLLY_SAMPLE_RATE,
        engine: str = POLLY_ENGINE
    ):
        self.region = region
        self.voice_id = voice_id
        self.sample_rate = sample_rate
        self.engine = engine
        self._client = None
    
    @property
    def client(self):
        """Polly クライアント（遅延初期化）"""
        if self._client is None:
            self._client = boto3.client("polly", region_name=self.region)
        return self._client
    
    def synthesize_pcm(self, text: str) -> bytes:
        """
        テキストを PCM 音声に変換（同期）
        
        Args:
            text: 合成するテキスト
        
        Returns:
            PCM 音声データ
        """
        try:
            response = self.client.synthesize_speech(
                Text=text,
                VoiceId=self.voice_id,
                OutputFormat="pcm",
                SampleRate=str(self.sample_rate),
                Engine=self.engine
            )
            return response["AudioStream"].read()
        except Exception as e:
            print(f"Polly error: {e}")
            raise
    
    async def synthesize_pcm_async(self, text: str) -> bytes:
        """
        テキストを PCM 音声に変換（非同期）
        
        Args:
            text: 合成するテキスト
        
        Returns:
            PCM 音声データ
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self.synthesize_pcm, text)
    
    def synthesize_mp3(self, text: str) -> bytes:
        """
        テキストを MP3 音声に変換（同期）
        
        Args:
            text: 合成するテキスト
        
        Returns:
            MP3 音声データ
        """
        try:
            response = self.client.synthesize_speech(
                Text=text,
                VoiceId=self.voice_id,
                OutputFormat="mp3",
                Engine=self.engine
            )
            return response["AudioStream"].read()
        except Exception as e:
            print(f"Polly error: {e}")
            raise
    
    async def synthesize_mp3_async(self, text: str) -> bytes:
        """
        テキストを MP3 音声に変換（非同期）
        
        Args:
            text: 合成するテキスト
        
        Returns:
            MP3 音声データ
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self.synthesize_mp3, text)
    
    def synthesize_ssml(
        self,
        ssml: str,
        output_format: str = "pcm"
    ) -> bytes:
        """
        SSML を音声に変換（同期）
        
        Args:
            ssml: SSML マークアップ
            output_format: 出力形式（pcm, mp3, ogg_vorbis）
        
        Returns:
            音声データ
        """
        try:
            params = {
                "Text": ssml,
                "TextType": "ssml",
                "VoiceId": self.voice_id,
                "OutputFormat": output_format,
                "Engine": self.engine
            }
            
            if output_format == "pcm":
                params["SampleRate"] = str(self.sample_rate)
            
            response = self.client.synthesize_speech(**params)
            return response["AudioStream"].read()
        except Exception as e:
            print(f"Polly SSML error: {e}")
            raise
    
    async def synthesize_ssml_async(
        self,
        ssml: str,
        output_format: str = "pcm"
    ) -> bytes:
        """
        SSML を音声に変換（非同期）
        
        Args:
            ssml: SSML マークアップ
            output_format: 出力形式
        
        Returns:
            音声データ
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor,
            self.synthesize_ssml,
            ssml,
            output_format
        )
    
    def get_voices(self, language_code: str = "ja-JP") -> list:
        """
        利用可能な音声一覧を取得
        
        Args:
            language_code: 言語コード
        
        Returns:
            音声リスト
        """
        try:
            response = self.client.describe_voices(LanguageCode=language_code)
            return response.get("Voices", [])
        except Exception as e:
            print(f"Polly describe_voices error: {e}")
            return []
    
    @staticmethod
    def wrap_ssml(
        text: str,
        rate: str = "medium",
        pitch: str = "medium",
        volume: str = "medium"
    ) -> str:
        """
        テキストを SSML でラップ
        
        Args:
            text: テキスト
            rate: 速度（x-slow, slow, medium, fast, x-fast）
            pitch: ピッチ（x-low, low, medium, high, x-high）
            volume: 音量（silent, x-soft, soft, medium, loud, x-loud）
        
        Returns:
            SSML 文字列
        """
        return f"""<speak>
            <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
                {text}
            </prosody>
        </speak>"""
    
    @staticmethod
    def add_pause(text: str, pause_ms: int = 500) -> str:
        """
        テキストにポーズを追加
        
        Args:
            text: テキスト
            pause_ms: ポーズ（ミリ秒）
        
        Returns:
            SSML 文字列
        """
        return f'<speak>{text}<break time="{pause_ms}ms"/></speak>'


class PollySession:
    """
    Polly セッション（キャッシュ付き）
    """
    
    def __init__(self, service: Optional[PollyService] = None):
        self.service = service or PollyService()
        self._cache: dict = {}
        self._lock = asyncio.Lock()
    
    async def synthesize(self, text: str, use_cache: bool = True) -> bytes:
        """
        テキストを音声に変換（キャッシュ付き）
        
        Args:
            text: テキスト
            use_cache: キャッシュを使用するか
        
        Returns:
            PCM 音声データ
        """
        cache_key = text.strip()
        
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        async with self._lock:
            # ダブルチェック
            if use_cache and cache_key in self._cache:
                return self._cache[cache_key]
            
            audio = await self.service.synthesize_pcm_async(text)
            
            if use_cache:
                self._cache[cache_key] = audio
            
            return audio
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._cache.clear()


# デフォルトサービスインスタンス
polly_service = PollyService()
