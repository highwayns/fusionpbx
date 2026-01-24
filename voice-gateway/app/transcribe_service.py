"""
Voice Gateway - Amazon Transcribe Service
音声認識 (STT) サービス
"""
import os
import asyncio
from typing import Optional, Callable, Awaitable
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
TRANSCRIBE_LANGUAGE_CODE = os.getenv("TRANSCRIBE_LANGUAGE_CODE", "ja-JP")
TRANSCRIBE_SAMPLE_RATE = int(os.getenv("TRANSCRIBE_SAMPLE_RATE", "16000"))
AUDIO_QUEUE_MAX = int(os.getenv("AUDIO_QUEUE_MAX", "50"))

# Amazon Transcribe Streaming SDK
try:
    from amazon_transcribe.client import TranscribeStreamingClient
    from amazon_transcribe.handlers import TranscriptResultStreamHandler
    from amazon_transcribe.model import TranscriptEvent
    TRANSCRIBE_AVAILABLE = True
except ImportError:
    TranscribeStreamingClient = None
    TranscriptResultStreamHandler = object
    TranscriptEvent = object
    TRANSCRIBE_AVAILABLE = False


class TranscriptHandler(TranscriptResultStreamHandler):
    """
    Transcribe 結果ハンドラ
    Final transcript のみをコールバックに渡す
    """
    
    def __init__(self, output_stream, on_final_text: Callable[[str], Awaitable[None]]):
        super().__init__(output_stream)
        self.on_final_text = on_final_text
        self._partial_text = ""
    
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        """
        Transcript イベントを処理
        """
        for result in transcript_event.transcript.results:
            if result.is_partial:
                # Partial 結果（進行中）
                for alt in result.alternatives:
                    self._partial_text = (alt.transcript or "").strip()
            else:
                # Final 結果（確定）
                for alt in result.alternatives:
                    text = (alt.transcript or "").strip()
                    if text:
                        await self.on_final_text(text)
                self._partial_text = ""


class TranscribeService:
    """
    Amazon Transcribe Streaming サービス
    """
    
    def __init__(
        self,
        region: str = AWS_REGION,
        language_code: str = TRANSCRIBE_LANGUAGE_CODE,
        sample_rate: int = TRANSCRIBE_SAMPLE_RATE
    ):
        self.region = region
        self.language_code = language_code
        self.sample_rate = sample_rate
    
    @property
    def available(self) -> bool:
        """SDK が利用可能か"""
        return TRANSCRIBE_AVAILABLE
    
    async def start_stream(
        self,
        audio_queue: asyncio.Queue,
        on_final_text: Callable[[str], Awaitable[None]],
        on_error: Optional[Callable[[Exception], Awaitable[None]]] = None
    ):
        """
        ストリーミング音声認識を開始
        
        Args:
            audio_queue: 音声データキュー（bytes または None で終了）
            on_final_text: 確定テキストのコールバック
            on_error: エラーコールバック
        """
        if not TRANSCRIBE_AVAILABLE:
            raise RuntimeError(
                "amazon-transcribe SDK is not installed. "
                "Run: pip install amazon-transcribe"
            )
        
        client = TranscribeStreamingClient(region=self.region)
        
        try:
            stream = await client.start_stream_transcription(
                language_code=self.language_code,
                media_sample_rate_hz=self.sample_rate,
                media_encoding="pcm",
            )
            
            # 音声データ送信タスク
            async def audio_writer():
                while True:
                    chunk = await audio_queue.get()
                    if chunk is None:
                        # 終了シグナル
                        break
                    await stream.input_stream.send_audio_event(audio_chunk=chunk)
                await stream.input_stream.end_stream()
            
            writer_task = asyncio.create_task(audio_writer())
            
            # 結果ハンドラ
            handler = TranscriptHandler(stream.output_stream, on_final_text)
            await handler.handle_events()
            
            await writer_task
            
        except Exception as e:
            if on_error:
                await on_error(e)
            else:
                print(f"Transcribe error: {e}")
                raise


class TranscribeSession:
    """
    Transcribe セッション（1通話分）
    """
    
    def __init__(
        self,
        service: Optional[TranscribeService] = None,
        language_code: str = TRANSCRIBE_LANGUAGE_CODE
    ):
        self.service = service or TranscribeService(language_code=language_code)
        self.audio_queue: asyncio.Queue = asyncio.Queue(maxsize=AUDIO_QUEUE_MAX)
        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(
        self,
        on_final_text: Callable[[str], Awaitable[None]],
        on_error: Optional[Callable[[Exception], Awaitable[None]]] = None
    ):
        """
        セッションを開始
        
        Args:
            on_final_text: 確定テキストのコールバック
            on_error: エラーコールバック
        """
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(
            self.service.start_stream(
                audio_queue=self.audio_queue,
                on_final_text=on_final_text,
                on_error=on_error
            )
        )
    
    async def feed_audio(self, audio_data: bytes):
        """
        音声データをフィード
        
        Args:
            audio_data: PCM 音声データ
        """
        if not self._running:
            return
        
        try:
            self.audio_queue.put_nowait(audio_data)
        except asyncio.QueueFull:
            # キューが満杯の場合はドロップ（レイテンシ維持）
            pass
    
    async def stop(self, timeout: float = 5.0):
        """
        セッションを停止
        
        Args:
            timeout: 停止タイムアウト（秒）
        """
        if not self._running:
            return
        
        self._running = False
        
        try:
            await self.audio_queue.put(None)
        except Exception:
            pass
        
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=timeout)
            except asyncio.TimeoutError:
                self._task.cancel()
            except Exception:
                pass
    
    @property
    def running(self) -> bool:
        """セッションが実行中か"""
        return self._running


# デフォルトサービスインスタンス
transcribe_service = TranscribeService()
