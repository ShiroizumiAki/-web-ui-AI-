"""
多模态 AI 平台的全局配置管理。
使用 st.session_state 实现跨页面持久化，使用 .env 文件提供默认值。
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# 默认配置
DEFAULTS = {
    "deepseek": {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "model": os.getenv("DEEPSEEK_MODEL", ""),
    },
    "volcengine": {
        "api_key": os.getenv("VOLCENGINE_API_KEY", ""),
        "base_url": os.getenv("VOLCENGINE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
        "vision_model": os.getenv("VOLCENGINE_VISION_MODEL", ""),
    },
}

CONFIG_KEYS = ["deepseek", "volcengine"]


def init_config():
    """如果尚未设置，使用默认配置初始化 session state。"""
    for key in CONFIG_KEYS:
        if key not in st.session_state:
            st.session_state[key] = DEFAULTS[key].copy()

    if "custom_providers" not in st.session_state:
        st.session_state["custom_providers"] = {}

    if "prompts" not in st.session_state:
        st.session_state["prompts"] = {}

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []


def get_config(platform: str) -> dict:
    """获取指定平台的配置。"""
    init_config()
    return st.session_state.get(platform, DEFAULTS.get(platform, {}))


def set_config(platform: str, key: str, value: str):
    """设置指定的配置值。"""
    init_config()
    if platform in st.session_state:
        st.session_state[platform][key] = value


def get_deepseek_client():
    """获取兼容 OpenAI 格式的 DeepSeek 客户端。"""
    from openai import OpenAI
    cfg = get_config("deepseek")
    return OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])


def get_volcengine_client():
    """获取兼容 OpenAI 格式的火山引擎 Ark 客户端。"""
    from openai import OpenAI
    cfg = get_config("volcengine")
    return OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])


def is_api_configured(platform: str = None, config_dict: dict = None) -> bool:
    """检查指定平台的 API Key 是否已配置。

    可以通过平台名称调用，也可以直接传入配置字典调用。
    """
    if config_dict is not None:
        return bool(config_dict.get("api_key", "").strip())
    cfg = get_config(platform)
    return bool(cfg.get("api_key", "").strip())


# 自定义提供商管理

def init_custom_providers():
    """初始化自定义提供商存储。"""
    if "custom_providers" not in st.session_state:
        st.session_state["custom_providers"] = {}


def get_custom_providers() -> dict:
    """获取所有自定义提供商，格式为 {名称: {api_key, base_url, model}}。"""
    init_custom_providers()
    return st.session_state["custom_providers"]


def add_custom_provider(name: str, api_key: str, base_url: str, model: str):
    """添加或更新自定义提供商。"""
    init_custom_providers()
    st.session_state["custom_providers"][name] = {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


def delete_custom_provider(name: str):
    """按名称删除自定义提供商。"""
    init_custom_providers()
    if name in st.session_state["custom_providers"]:
        del st.session_state["custom_providers"][name]


def get_client(api_key: str, base_url: str):
    """获取适用于任意提供商的通用 OpenAI 兼容客户端。"""
    from openai import OpenAI
    return OpenAI(api_key=api_key, base_url=base_url)
