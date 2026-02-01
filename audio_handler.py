"""
音频文件处理器 - mutagen 封装

支持 MP3/WAV/FLAC 文件的元数据读取和写入
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Any

from mutagen import File as MutagenFile # type: ignore
from mutagen.id3 import ID3, USLT, TIT2, TPE1, TALB, TCON, ID3NoHeaderError # type: ignore

AudioType = Literal["mp3", "wav", "flac"]

format_map: dict[str, AudioType] = {
    ".mp3": "mp3",
    ".wav": "wav",
    ".wave": "wav",
    ".flac": "flac",
}

@dataclass
class SongInfo:
    """歌曲信息数据类"""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None


@dataclass
class Lyrics:
    """歌词数据类"""
    text: str
    lang: str = "eng"  # ISO 639-2 语言代码


class AudioHandlerError(Exception):
    """音频处理器基础异常"""
    pass


class UnsupportedFormatError(AudioHandlerError):
    """不支持的文件格式"""
    pass


class FileNotFoundError(AudioHandlerError):
    """文件不存在"""
    pass


class AudioHandler:
    """音频文件处理器"""

    SUPPORTED_FORMATS: set[AudioType] = {"mp3", "wav", "flac"}

    def __init__(self, file_path: str | Path) -> None:
        """
        初始化音频处理器

        Args:
            file_path: 音频文件路径

        Raises:
            FileNotFoundError: 文件不存在
            UnsupportedFormatError: 不支持的文件格式
        """
        self.file_path = Path(file_path).resolve()

        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        self.file_type = self._detect_format()
        if self.file_type not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(
                f"不支持的格式: {self.file_type}. 支持: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # 音频类
        self._audio: Any = None

    def _detect_format(self) -> Optional[AudioType]:
        """检测文件格式"""
        suffix = self.file_path.suffix.lower()
        return format_map.get(suffix)

    @property
    def audio(self) -> Any: # 返回音频
        """懒加载音频文件"""
        if self._audio is None:
            self._audio = MutagenFile(self.file_path)
        return self._audio

    # ========== 歌曲信息操作 ==========

    def get_song_info(self) -> SongInfo:
        """
        获取歌曲信息

        Returns:
            SongInfo: 包含标题、艺术家、专辑、流派的信息
        """
        if self.file_type == "mp3":
            return self._get_song_info_mp3()
        elif self.file_type == "flac":
            return self._get_song_info_flac()
        elif self.file_type == "wav":
            return self._get_song_info_wav()
        else:
            return SongInfo()

    def _get_song_info_mp3(self) -> SongInfo:
        """从 MP3 文件获取歌曲信息"""
        info = SongInfo()

        try:
            id3 = ID3(self.file_path)
            info.title = str(id3.get("TIT2", ""))
            info.artist = str(id3.get("TPE1", ""))
            info.album = str(id3.get("TALB", ""))
            info.genre = str(id3.get("TCON", ""))
        except ID3NoHeaderError:
            pass  # 没有 ID3 标签

        return info

    def _get_song_info_flac(self) -> SongInfo:
        """从 FLAC 文件获取歌曲信息"""
        info = SongInfo()
        audio = self.audio

        info.title = audio.get("TITLE", [None])[0]
        info.artist = audio.get("ARTIST", [None])[0]
        info.album = audio.get("ALBUM", [None])[0]
        info.genre = audio.get("GENRE", [None])[0]

        return info

    def _get_song_info_wav(self) -> SongInfo:
        """从 WAV 文件获取歌曲信息"""
        info = SongInfo()
        audio = self.audio

        if hasattr(audio, "info"):
            info.title = getattr(audio.info, "title", None)
            info.artist = getattr(audio.info, "artist", None)
            info.album = getattr(audio.info, "album", None)
            info.genre = getattr(audio.info, "genre", None)

        return info

    def set_song_info(self, song_info: SongInfo) -> None:
        """
        设置歌曲信息

        Args:
            song_info: SongInfo 对象
        """
        if self.file_type == "mp3":
            self._set_song_info_mp3(song_info)
        elif self.file_type == "flac":
            self._set_song_info_flac(song_info)
        elif self.file_type == "wav":
            self._set_song_info_wav(song_info)

        # 保存更改
        self.audio.save()

    def _set_song_info_mp3(self, song_info: SongInfo) -> None:
        """设置 MP3 文件的歌曲信息"""
        try:
            id3 = ID3(self.file_path)
        except ID3NoHeaderError:
            id3 = ID3()

        if song_info.title is not None:
            id3["TIT2"] = TIT2(encoding=3, text=song_info.title)
        if song_info.artist is not None:
            id3["TPE1"] = TPE1(encoding=3, text=song_info.artist)
        if song_info.album is not None:
            id3["TALB"] = TALB(encoding=3, text=song_info.album)
        if song_info.genre is not None:
            id3["TCON"] = TCON(encoding=3, text=song_info.genre)

        id3.save(self.file_path)

    def _set_song_info_flac(self, song_info: SongInfo) -> None:
        """设置 FLAC 文件的歌曲信息"""
        audio = self.audio

        if song_info.title is not None:
            audio["TITLE"] = song_info.title
        if song_info.artist is not None:
            audio["ARTIST"] = song_info.artist
        if song_info.album is not None:
            audio["ALBUM"] = song_info.album
        if song_info.genre is not None:
            audio["GENRE"] = song_info.genre

        audio.save()

    def _set_song_info_wav(self, song_info: SongInfo) -> None:
        """设置 WAV 文件的歌曲信息"""
        audio = self.audio

        if hasattr(audio, "info"):
            if song_info.title is not None:
                audio.info.title = song_info.title
            if song_info.artist is not None:
                audio.info.artist = song_info.artist
            if song_info.album is not None:
                audio.info.album = song_info.album
            if song_info.genre is not None:
                audio.info.genre = song_info.genre

        audio.save()

    # ========== 歌词操作 ==========

    def get_lyrics(self) -> Optional[Lyrics]:
        """
        获取歌词

        Returns:
            Lyrics 对象，失败返回 None
        """
        if self.file_type == "mp3":
            return self._get_lyrics_mp3()
        elif self.file_type == "flac":
            return self._get_lyrics_flac()
        elif self.file_type == "wav":
            return self._get_lyrics_wav()
        return None

    def _get_lyrics_mp3(self) -> Optional[Lyrics]:
        """从 MP3 文件获取歌词"""
        try:
            id3 = ID3(self.file_path)
            uslt = id3.getall("USLT")
            if uslt:
                first_uslt = uslt[0]
                return Lyrics(text=str(first_uslt.text), lang=first_uslt.lang)
        except ID3NoHeaderError:
            pass
        return None

    def _get_lyrics_flac(self) -> Optional[Lyrics]:
        """从 FLAC 文件获取歌词"""
        audio = self.audio
        lyrics_list = audio.get("LYRICS", [])

        if lyrics_list:
            return Lyrics(text=lyrics_list[0], lang="eng")

        # 也尝试从 DESCRIPTION 获取
        desc_list = audio.get("DESCRIPTION", [])
        if desc_list:
            return Lyrics(text=desc_list[0], lang="eng")

        return None

    def _get_lyrics_wav(self) -> Optional[Lyrics]:
        """从 WAV 文件获取歌词"""
        # WAV 不标准支持歌词，使用 INFO 标签
        audio = self.audio

        if hasattr(audio, "info"):
            lyrics = getattr(audio.info, "lyrics", None)
            if lyrics:
                return Lyrics(text=lyrics, lang="eng")

        return None

    def set_lyrics(self, lyrics: str | Lyrics) -> None:
        """
        设置歌词

        Args:
            lyrics: 歌词文本或 Lyrics 对象
        """
        if isinstance(lyrics, str):
            lyrics_obj = Lyrics(text=lyrics)
        else:
            lyrics_obj = lyrics

        if self.file_type == "mp3":
            self._set_lyrics_mp3(lyrics_obj)
        elif self.file_type == "flac":
            self._set_lyrics_flac(lyrics_obj)
        elif self.file_type == "wav":
            self._set_lyrics_wav(lyrics_obj)

        self.audio.save()

    def _set_lyrics_mp3(self, lyrics: Lyrics) -> None:
        """设置 MP3 文件的歌词"""
        try:
            id3 = ID3(self.file_path)
        except ID3NoHeaderError:
            id3 = ID3()

        # 删除现有的歌词标签
        id3.delall("USLT")

        # 添加新歌词
        id3["USLT"] = USLT(
            encoding=3,
            lang=lyrics.lang,
            desc="Lyrics",
            text=lyrics.text,
        )

        id3.save(self.file_path)

    def _set_lyrics_flac(self, lyrics: Lyrics) -> None:
        """设置 FLAC 文件的歌词"""
        audio = self.audio
        audio["LYRICS"] = lyrics.text
        audio.save()

    def _set_lyrics_wav(self, lyrics: Lyrics) -> None:
        """设置 WAV 文件的歌词"""
        # WAV 不标准支持歌词，使用 LIST 标签
        audio = self.audio

        if hasattr(audio, "info"):
            audio.info.lyrics = lyrics.text

        audio.save()

    # ========== 辅助方法 ==========

    def get_audio_info(self) -> dict:
        """
        获取音频文件的详细信息

        Returns:
            包含格式、时长、比特率等信息的字典
        """
        info = {
            "file_path": str(self.file_path),
            "format": self.file_type,
            "file_size": os.path.getsize(self.file_path),
        }

        if self.audio.info:
            if hasattr(self.audio.info, "length"):
                info["duration"] = self.audio.info.length  # 秒
            if hasattr(self.audio.info, "bitrate"):
                info["bitrate"] = self.audio.info.bitrate  # bps
            if hasattr(self.audio.info, "sample_rate"):
                info["sample_rate"] = self.audio.info.sample_rate

        return info
