"""
音频文件处理器 - mutagen 封装

支持 MP3/FLAC 文件的元数据读取和写入
"""
from dataclasses import dataclass
from typing import Optional, Union, Any, Never
from pathlib import Path
from enum import Enum
import logging

from mutagen import File # type: ignore
from mutagen.mp3 import MP3
from mutagen.flac import FLAC

logger = logging.getLogger(__name__)

class AudioType(Enum):
    FLAC = 'flac'
    MP3 = 'mp3'

@dataclass
class AudioMetadata:
    """音频文件元数据"""
    title: Optional[str] = None              # 标题
    artist: Optional[str] = None             # 艺术家
    album: Optional[str] = None              # 专辑
    albumartist: Optional[str] = None        # 专辑艺术家
    genre: Optional[str] = None              # 流派
    year: Optional[str] = None               # 日期/年份
    track: Optional[str] = None              # 轨道号
    disc: Optional[str] = None               # 碟号
    comment: Optional[str] = None            # 注释
    lyrics: Optional[str] = None             # 歌词
    
    # 音频技术信息
    duration: Optional[float] = None         # 时长（秒）
    sample_rate: Optional[int] = None        # 采样率
    bitrate: Optional[int] = None            # 比特率（bps）
    bits_per_sample: Optional[int] = None    # 位深度（无损格式）
    channels: Optional[int] = None           # 声道数

class AudioHandler:
    """
    音频处理器
    """
    def __init__(self, path: Union[Path, str]):
        self.path = Path(path).resolve()
        self.audio: Any = File(self.path)
        self.audio_type: Optional[AudioType] = None
        self.metadata: Optional[AudioMetadata] = None
        self._validate_audio_type()
        self._load_metadata()

    def _validate_audio_type(self):
        if isinstance(self.audio, MP3):
            self.audio_type = AudioType.MP3
        elif isinstance(self.audio, FLAC):
            self.audio_type = AudioType.FLAC
        else:
            raise ValueError(f"不支持的音频格式，请确认格式为mp3或flac，文件路径：{self.path}")

    def _load_metadata(self):
        if self.audio is not None:
            self.metadata = AudioMetadata(
                title=self.audio.get('title'),
                artist=self.audio.get('artist'),
                album=self.audio.get('album'),
                albumartist=self.audio.get('albumartist'),
                genre=self.audio.get('genre'),
                year=self.audio.get('date'),
                track=self.audio.get('tracknumber'),
                disc=self.audio.get('discnumber'),
                comment=self.audio.get('comment'),
                lyrics=self._extract_lyrics(),
                duration=self.audio.info.get("length"),
                sample_rate=self.audio.info.get("sample_rate"),
                bitrate=self.audio.info.get("bitrate"),
                bits_per_sample=self.audio.info.get("bits_per_sample"),
                channels=self.audio.info.get("channels"),
            )

    def _extract_lyrics(self) -> Optional[str]:
        lyrics: Optional[str] = None
        if self.audio is not None:
            audio_type = AudioType(self.audio_type)
            match audio_type:
                case AudioType.FLAC:
                    lyrics = self.audio.get('lyrics') # flac格式直接获取歌词
                case AudioType.MP3:
                    # MP3: 遍历 frames 查找 USLT 帧
                    for frame in self.audio.values():
                        # USLT = Unsynchronised Lyrics/Text
                        if hasattr(frame, 'frameid') and frame.frameid == 'USLT':
                            lyrics =  frame.text
                case _ as unreachable:
                    never_type: Never = unreachable
                    raise ValueError(f"提取歌词时出现未实现的格式{never_type}")
        else:
            raise RuntimeError('audio未正确初始化，请检查代码逻辑。')
        return lyrics

    