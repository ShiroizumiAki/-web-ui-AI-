"""
多模态AI智能助手 - 首页
一站式AI创作与交互平台
"""
import streamlit as st

# 页面配置必须在最前面
st.set_page_config(
    page_title="多模态AI智能助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui_components import (
    inject_css, render_sidebar, render_feature_card,
    render_step_card, render_tech_card,
)
from utils.config import init_config, is_api_configured
from utils.prompts import init_prompts


def main():
    inject_css()
    init_config()
    init_prompts()

    # ---- 侧边栏 ----
    render_sidebar()

    # ---- 主横幅 ----
    st.markdown("""
    <div class="hero-banner">
        <div class="title">🤖 多模态AI智能助手</div>
        <div class="subtitle">
            一站式AI创作与交互平台，七大核心功能覆盖文本、图像、语音、视频全模态
        </div>
        <div class="quick-links">
            <span class="quick-link">📚 RAG文档问答</span>
            <span class="quick-link">🎨 文生图</span>
            <span class="quick-link">🖼️ 图片解读</span>
            <span class="quick-link">🎬 图生视频</span>
            <span class="quick-link">🔊 文生音频</span>
            <span class="quick-link">🎙️ 音频生文</span>
            <span class="quick-link">📊 数据分析</span>
            <span class="quick-link">📁 知识库管理</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- 功能导航 ----
    st.markdown("""
    <div class="section-header">
        <span class="icon">🎯</span>
        <span class="title">功能导航</span>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("📁", "知识库管理", "创建知识库、上传私域文档，构建持久化的RAG知识库，为文档问答功能提供素材", "08_知识库管理"),
        ("📚", "RAG文档问答", "基于已上传的知识库或临时上传文档，进行智能检索增强生成问答，支持流式输出与来源引用", "01_RAG文档问答"),
        ("🎨", "文生图", "输入文字描述生成对应图片，支持多种风格预设、尺寸选择和批量生成", "02_文生图"),
        ("🖼️", "图片解读", "AI视觉分析图片内容，支持详细描述、构图分析、OCR文字提取、情感分析等模板", "03_图片解读"),
        ("🎬", "图生视频", "上传静态图片，AI自动生成动态效果视频，支持多种运动模板", "04_图生视频"),
        ("🔊", "文生音频", "文字转语音功能，提供6种可选音色，支持自定义语速和音量调节", "05_文生音频"),
    ]

    for row_start in range(0, len(features), 3):
        cols = st.columns(3)
        for i, (emoji, title, desc, page) in enumerate(features[row_start:row_start+3]):
            with cols[i]:
                render_feature_card(emoji, title, desc, page)

    # ---- 快速开始指南 ----
    st.markdown("""
    <div class="section-header">
        <span class="icon">🚀</span>
        <span class="title">快速开始</span>
    </div>
    """, unsafe_allow_html=True)

    qs1, qs2, qs3 = st.columns(3)
    with qs1:
        render_step_card(1, "step-1", "配置 API Key",
                        "前往系统设置页面，填写 DeepSeek 和火山引擎的 API Key，这是使用所有功能的前置条件。")
    with qs2:
        render_step_card(2, "step-2", "选择功能模块",
                        "点击上方功能卡片或使用左侧导航菜单，进入你想要使用的 AI 功能页面。")
    with qs3:
        render_step_card(3, "step-3", "开始创作",
                        "进入功能页面后，按照页面提示输入内容或上传文件，即可调用 AI 生成对应结果。")

    # ---- 技术栈 ----
    st.markdown("""
    <div class="section-header">
        <span class="icon">🔧</span>
        <span class="title">技术栈</span>
    </div>
    """, unsafe_allow_html=True)

    tc1, tc2, tc3, tc4, tc5, tc6 = st.columns(6)
    techs = [
        (tc1, "大语言模型", "badge-blue", "DeepSeek", "deepseek-chat"),
        (tc2, "视觉模型", "badge-purple", "豆包视觉", "doubao-seed-2-0-pro"),
        (tc3, "向量数据库", "badge-yellow", "ChromaDB", "bge-small-zh-v1.5"),
        (tc4, "Web框架", "badge-green", "Streamlit", "多页面应用"),
        (tc5, "API平台", "badge-pink", "火山引擎", "Ark + 语音技术"),
        (tc6, "数据处理", "badge-cyan", "Pandas+LangChain", "文档解析处理"),
    ]
    for col, badge, cls, name, detail in techs:
        with col:
            render_tech_card(badge, cls, name, detail)

    # ---- 支持的文件格式 ----
    st.markdown("""
    <div class="section-header">
        <span class="icon">📂</span>
        <span class="title">支持的文件格式</span>
    </div>
    """, unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.markdown("""
        <div class="tech-card">
            <div class="badge badge-blue">📄 文档类</div>
            <div class="name" style="font-size:13px; margin-top:8px;">PDF / TXT / DOCX</div>
            <div class="name" style="font-size:13px;">MD / CSV / XLSX</div>
            <div class="detail">供 RAG 问答、文档解析使用</div>
        </div>
        """, unsafe_allow_html=True)
    with fc2:
        st.markdown("""
        <div class="tech-card">
            <div class="badge badge-purple">🖼️ 图片类</div>
            <div class="name" style="font-size:13px; margin-top:8px;">JPG / PNG / WEBP</div>
            <div class="name" style="font-size:13px;">GIF / BMP</div>
            <div class="detail">供图片解读、图生视频使用</div>
        </div>
        """, unsafe_allow_html=True)
    with fc3:
        st.markdown("""
        <div class="tech-card">
            <div class="badge badge-green">🎵 音频类</div>
            <div class="name" style="font-size:13px; margin-top:8px;">WAV / MP3 / FLAC</div>
            <div class="name" style="font-size:13px;">M4A / OGG</div>
            <div class="detail">供音频转文字功能使用</div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
