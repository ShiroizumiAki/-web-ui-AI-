# 多模态 AI 智能助手

一站式 AI 创作与交互平台，覆盖文本、图像、语音、视频全模态的智能助手 Web 应用。

另：需要自行准备API密钥。

~~言简意赅来说就是个意义不明的不时尚小垃圾~~

## 功能概览

| 功能 | 说明 |
|------|------|
| RAG 文档问答 | 基于向量检索的智能文档问答，支持多格式文档 |
| 文生图 | 文字描述生成图像，多风格预设 |
| 图片解读 | AI 视觉分析（描述/构图/OCR/情感） |
| 图生视频 | 静态图片生成动态视频 |
| 文生音频 | 文字转语音（TTS），6 种音色 |
| 音频生文 | 语音转文字（ASR），支持字幕导出 |
| Excel 助手 | 数据分析、可视化与 AI 洞察 |
| 知识库管理 | 文档向量化存储与语义检索 |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key（可选，也可在应用内配置）
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 3. 启动
streamlit run app.py

# 4. 浏览器打开 http://localhost:8501
```

## API 配置

项目默认支持 **DeepSeek**（LLM）和 **火山引擎**（视觉/图像/视频/TTS/ASR），同时支持自行添加任意 **OpenAI 兼容的 LLM 提供商**（如 OpenAI、Ollama、OpenRouter 等）。

API Key 可通过两种方式配置：
- 创建 `.env` 文件设置环境变量
- 在应用内「系统设置 → API 配置」页面直接输入

## 技术栈

- **框架**: Streamlit
- **LLM**: DeepSeek + 自定义 OpenAI 兼容模型
- **视觉**: 火山引擎豆包视觉
- **图像/视频生成**: 火山引擎 Seedream / Seedance
- **语音**: 火山引擎 TTS / ASR
- **向量数据库**: ChromaDB
- **嵌入模型**: BAAI/bge-small-zh-v1.5（本地运行）
- **数据处理**: Pandas + Plotly

## 项目结构

```
├── app.py                  # 首页入口
├── requirements.txt        # 依赖
├── pages/                  # 功能页面（9 个）
│   ├── 01_RAG文档问答.py
│   ├── 02_文生图.py
│   ├── 03_图片解读.py
│   ├── 04_图生视频.py
│   ├── 05_文生音频.py
│   ├── 06_音频生文.py
│   ├── 07_Excel助手.py
│   ├── 08_知识库管理.py
│   └── 09_系统设置.py
└── utils/                  # 工具模块
    ├── api_client.py       # API 客户端封装
    ├── config.py           # 配置管理
    ├── prompts.py          # 提示词模板
    ├── rag.py              # RAG 流水线
    ├── knowledge_base.py   # 知识库管理
    └── ui_components.py    # UI 组件
```

## 环境要求

- Python 3.12+
- 首次运行时会自动下载 BGE 嵌入模型（约 100MB）
