# 音乐歌词编辑软件 - 开发计划

## 项目概述

开发一款 GUI 音乐歌词编辑工具，支持 MP3/WAV/FLAC 格式，为音乐文件内嵌歌词和歌曲信息。

## 技术选型

| 功能 | 技术方案 |
|------|----------|
| GUI 界面 | customtkinter |
| 音频处理 | mutagen |
| 音乐播放 | pygame |
| 歌词获取 | 网易云音乐 API |
| HTTP 请求 | requests |

## 功能需求

### 核心功能

1. **文件导入** - 导入音乐文件（支持 MP3、WAV、FLAC 格式）
2. **在线获取** - 通过网易云音乐 API 获取歌词和歌曲信息
3. **智能排序** - 对多个版本的歌词和歌曲信息进行置信度排序
4. **播放预览** - 播放音乐并展示歌词进度
5. **选择应用** - 选择性应用歌曲信息和歌词（全部或部分）
6. **手动编辑** - 支持手动输入和编辑歌词
7. **保存文件** - 将歌词和歌曲信息嵌入并保存到源文件

### 歌词格式

- 纯文本歌词（嵌入音乐文件元数据）

### 音频格式支持

- MP3
- WAV
- FLAC

## 项目结构

```
music_lyric_editor/
├── core/                    # 核心功能模块
│   ├── audio_handler.py     # 音频文件读写（mutagen 封装）
│   ├── lyric_fetcher.py     # 歌词获取（网易云音乐 API）
│   ├── player.py            # 音乐播放控制
│   └── matcher.py           # 智能匹配排序
│
├── ui/                      # GUI 界面模块
│   ├── main_window.py       # 主窗口
│   ├── player_panel.py      # 播放控制面板
│   ├── file_list.py         # 文件列表
│   ├── lyric_selector.py    # 歌词选择器（多版本）
│   └── editor.py            # 手动编辑
│
├── models/                  # 数据模型
│   ├── song.py              # 歌曲信息模型
│   └── lyric.py             # 歌词模型
│
└── main.py                  # 程序入口
```

## 数据模型设计

### SongInfo（歌曲信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| title | str | 歌名 |
| artist | str | 歌手 |
| album | str | 专辑 |
| duration | int | 时长（秒） |

### LyricEntry（歌词条目）

| 字段 | 类型 | 说明 |
|------|------|------|
| text | str | 歌词文本 |
| source | str | 来源（API/手动） |
| timestamp | float | 时间戳（可选，LRC 格式用） |
| confidence | float | 匹配置信度 |

### LyricVersion（歌词版本）

| 字段 | 类型 | 说明 |
|------|------|------|
| source_name | str | 来源名称（如"网易云音乐"） |
| lyrics | List[LyricEntry] | 歌词列表 |
| song_info | SongInfo | 对应的歌曲信息 |
| confidence | float | 整体匹配置信度 |

## 实施阶段

### 第一阶段：基础框架

- 创建项目目录结构
- 配置 pyproject.toml 依赖
- 搭建基础代码框架

### 第二阶段：核心模块

- 实现 audio_handler.py（mutagen 封装）
  - 读取 MP3/WAV/FLAC 文件元数据
  - 读取/写入歌词到文件
  - 读取/写入歌曲信息到文件

- 实现 lyric_fetcher.py（网易云音乐 API）
  - 搜索歌曲
  - 获取歌词
  - 获取歌曲信息

- 实现 matcher.py（智能匹配排序）
  - 计算歌曲信息相似度
  - 计算歌词匹配置信度
  - 按置信度排序多个版本

### 第三阶段：播放器

- 实现 player.py（pygame）
  - 加载和播放音乐文件
  - 获取播放进度
  - 播放/暂停/停止控制

### 第四阶段：GUI 开发

- 实现 main_window.py（主窗口）
- 实现 player_panel.py（播放控制）
- 实现 file_list.py（文件列表）
- 实现 lyric_selector.py（歌词选择）
- 实现 editor.py（手动编辑）

### 第五阶段：集成测试

- 端到端功能测试
- 各模块联调测试
- 修复问题和优化

## 用户操作流程

```
1. 导入音乐文件
        ↓
2. 自动在线获取 → 多版本歌词/信息列表
        ↓
3. 智能排序（置信度降序排列）
        ↓
4. 用户预览（播放试听）
        ↓
5. 选择/编辑 → 部分或全部应用
        ↓
6. 保存到源文件
```

## 依赖清单

```toml
[project]
name = "music-lyric-editor"
version = "0.1.0"
description = "GUI 音乐歌词编辑工具"
readme = "README.md"
requires-python = ">=3.12"

[dependencies]
customtkinter = ">=5.2.0"    # GUI 界面
mutagen = ">=1.47.0"         # 音频元数据处理
pygame = ">=2.5.0"           # 音乐播放
requests = ">=2.31.0"        # HTTP 请求
```

## 待确认事项

- [ ] 歌词嵌入标签格式（ID3v2 / FLAC Vorbis Comments / WAV INFO）
- [ ] 网易云 API 实现方式（第三方库封装 / 自行封装）
- [ ] 初期是否支持批量导入多文件