"""
统一的 API 客户端层，封装 DeepSeek、火山引擎 Ark 和火山引擎语音服务。
"""
import base64
import os
import time
import tempfile
from io import BytesIO

import streamlit as st

from utils.config import get_config, get_deepseek_client, get_volcengine_client

# ============================================================
# DeepSeek 大语言模型
# ============================================================

def call_deepseek(messages: list, stream: bool = False, model: str = None):
    """调用 DeepSeek 对话 API。返回 (内容, 错误) 元组。"""
    cfg = get_config("deepseek")
    if not cfg.get("api_key"):
        return None, "请先在系统设置中配置 DeepSeek API Key"

    client = get_deepseek_client()
    try:
        if stream:
            response = client.chat.completions.create(
                model=model or cfg.get("model", ""),
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=4096,
            )
            return response, None
        else:
            response = client.chat.completions.create(
                model=model or cfg.get("model", ""),
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
            )
            return response.choices[0].message.content, None
    except Exception as e:
        return None, f"DeepSeek API 调用失败: {str(e)}"


def call_deepseek_stream(messages: list, model: str = None):
    """流式生成器，用于逐块返回 DeepSeek 响应。"""
    response, error = call_deepseek(messages, stream=True, model=model)
    if error:
        yield f"错误: {error}"
        return
    try:
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"流式输出错误: {str(e)}"


# ============================================================
# 火山引擎 Ark - 视觉模型
# ============================================================

def _encode_image(image_data: bytes, mime_type: str = "image/jpeg") -> str:
    """将图片字节编码为 base64 数据 URI。"""
    b64 = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def call_vision(image_data: bytes, prompt: str, stream: bool = False,
                mime_type: str = "image/jpeg", model: str = None):
    """调用火山引擎 Ark 视觉模型分析图片。"""
    cfg = get_config("volcengine")
    if not cfg.get("api_key"):
        return None, "请先在系统设置中配置火山引擎 API Key"

    client = get_volcengine_client()
    data_uri = _encode_image(image_data, mime_type)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_uri}},
                {"type": "text", "text": prompt},
            ],
        }
    ]

    try:
        if stream:
            response = client.chat.completions.create(
                model=model or cfg.get("vision_model", ""),
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2048,
            )
            return response, None
        else:
            response = client.chat.completions.create(
                model=model or cfg.get("vision_model", ""),
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )
            return response.choices[0].message.content, None
    except Exception as e:
        return None, f"火山引擎视觉 API 调用失败: {str(e)}"


def call_vision_stream(image_data: bytes, prompt: str,
                       mime_type: str = "image/jpeg", model: str = None):
    """流式生成器，用于逐块返回视觉模型响应。"""
    response, error = call_vision(image_data, prompt, stream=True,
                                   mime_type=mime_type, model=model)
    if error:
        yield f"错误: {error}"
        return
    try:
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"流式输出错误: {str(e)}"


# ============================================================
# 火山引擎 Ark - 文生图
# ============================================================

def generate_image(prompt: str, size: str = "1024x1024", n: int = 1,
                   negative_prompt: str = "", style: str = ""):
    """
    使用火山引擎 Ark 生成图片。
    优先通过 seedream 模型生成图片，失败时回退到生成图片描述。
    """
    cfg = get_config("volcengine")
    if not cfg.get("api_key"):
        return None, "请先在系统设置中配置火山引擎 API Key"

    client = get_volcengine_client()

    # 构建增强提示词，包含风格和负面提示词
    full_prompt = prompt
    if style:
        full_prompt = f"{style}风格：{prompt}"
    if negative_prompt:
        full_prompt += f"。避免：{negative_prompt}"

    # 解析尺寸
    size_map = {
        "1024x1024": (1024, 1024),
        "720x1280": (720, 1280),
        "1280x720": (1280, 720),
    }
    width, height = size_map.get(size, (1024, 1024))

    # 尝试火山引擎 Ark 图片生成端点
    try:
        # 使用 images/generations 端点（兼容 OpenAI 格式）
        response = client.images.generate(
            model="doubao-seedream-3-0-250110",
            prompt=full_prompt,
            n=n,
            size=size,
        )
        urls = [img.url for img in response.data]
        return urls, None
    except Exception as e1:
        # 回退方案：尝试备用的端点格式
        try:
            import httpx
            resp = httpx.post(
                f"{cfg['base_url']}/images/generations",
                headers={
                    "Authorization": f"Bearer {cfg['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "doubao-seedream-3-0-250110",
                    "prompt": full_prompt,
                    "n": n,
                    "size": size,
                },
                timeout=120,
            )
            if resp.status_code == 200:
                data = resp.json()
                urls = [img["url"] for img in data.get("data", [])]
                if urls:
                    return urls, None
        except Exception:
            pass

        return None, f"文生图 API 调用失败: {str(e1)}"


# ============================================================
# 火山引擎 - TTS（文本转语音）
# ============================================================

# 音色映射：显示名称 -> 火山引擎音色 ID
VOICE_OPTIONS = {
    "温柔女声": "BV001_streaming",
    "活泼女声": "BV002_streaming",
    "知性女声": "BV003_streaming",
    "沉稳男声": "BV004_streaming",
    "阳光男声": "BV005_streaming",
    "磁性男声": "BV006_streaming",
}


def text_to_speech(text: str, voice: str = "温柔女声",
                   speed: float = 1.0, volume: float = 1.0):
    """
    使用火山引擎 TTS API 将文本转换为语音。
    返回 (音频字节, 错误) 元组。
    """
    cfg = get_config("volcengine")
    if not cfg.get("api_key"):
        return None, "请先在系统设置中配置火山引擎 API Key"

    voice_id = VOICE_OPTIONS.get(voice, "BV001_streaming")

    try:
        import httpx
        import json as json_mod

        resp = httpx.post(
            "https://openspeech.bytedance.com/api/v1/tts",
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "app": {"appid": cfg.get("tts_appid", ""), "token": "placeholder"},
                "user": {"uid": "streamlit_user"},
                "audio": {
                    "voice_type": voice_id,
                    "encoding": "mp3",
                    "speed_ratio": speed,
                    "volume_ratio": volume,
                    "rate": 24000,
                },
                "request": {
                    "text": text,
                    "text_type": "plain",
                    "operation": "query",
                },
            },
            timeout=60,
        )

        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 3000 and data.get("data"):
                audio_b64 = data["data"]
                return base64.b64decode(audio_b64), None
            else:
                return None, f"TTS 失败: {data.get('message', '未知错误')}"
        else:
            return None, f"TTS API 返回错误: HTTP {resp.status_code}"
    except Exception as e:
        return None, f"TTS 调用失败: {str(e)}"


# 火山引擎 - ASR（语音转文本）

def speech_to_text(audio_data: bytes, audio_format: str = "mp3",
                   language: str = "zh-cn"):
    """
    使用火山引擎 ASR API 将音频转录为文字。
    返回 (文本, 片段列表, 错误) 元组。
    segments: 包含 text、start、end 字段的字典列表
    """
    cfg = get_config("volcengine")
    if not cfg.get("api_key"):
        return None, None, "请先在系统设置中配置火山引擎 API Key"

    try:
        import httpx

        # 将音频保存到临时文件用于上传
        ext = audio_format if audio_format != "m4a" else "mp4"
        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as f:
            f.write(audio_data)
            tmp_path = f.name

        try:
            with open(tmp_path, "rb") as f:
                resp = httpx.post(
                    "https://openspeech.bytedance.com/api/v1/asr",
                    headers={
                        "Authorization": f"Bearer {cfg['api_key']}",
                    },
                    files={"audio": (f"audio.{ext}", f, f"audio/{ext}")},
                    data={
                        "language": language,
                        "enable_timestamps": "1",
                        "enable_words": "1",
                    },
                    timeout=120,
                )
        finally:
            os.unlink(tmp_path)

        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0 or "text" in data:
                full_text = data.get("text", "")
                segments = data.get("utterances", [])
                return full_text, segments, None
            else:
                return None, None, f"ASR 失败: {data.get('message', '未知错误')}"
        else:
            return None, None, f"ASR API 返回错误: HTTP {resp.status_code}"
    except Exception as e:
        return None, None, f"ASR 调用失败: {str(e)}"


# 嵌入模型（本地 sentence-transformers）

_embedding_model = None


def get_embedding_model():
    """懒加载 sentence-transformers 嵌入模型。"""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        model_name = "BAAI/bge-small-zh-v1.5"
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


class LocalEmbeddings:
    """兼容 LangChain 的嵌入模型包装器，底层使用 sentence-transformers。"""

    def embed_documents(self, texts: list) -> list:
        model = get_embedding_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list:
        model = get_embedding_model()
        embedding = model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()
