"""
RAG 文档问答页面
"""
import streamlit as st
import os
import tempfile
from pathlib import Path

st.set_page_config(page_title="RAG文档问答", page_icon="📚", layout="wide")

from utils.ui_components import inject_css, render_sidebar, render_chat_message, render_sources
from utils.config import init_config
from utils.prompts import init_prompts, get_templates
from utils.knowledge_base import list_knowledge_bases
from utils.rag import rag_query, rag_query_temp_file


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## 📚 RAG 文档问答")
    st.markdown("*基于知识库的智能检索增强生成问答，支持流式输出和来源引用*")
    st.markdown("---")

    # 初始化聊天历史
    if "rag_messages" not in st.session_state:
        st.session_state["rag_messages"] = []

    # ---- 侧边栏: 配置 ----
    with st.sidebar:
        st.markdown("### ⚙️ 问答配置")

        mode = st.radio("文档来源", ["📁 使用已有知识库", "📄 临时上传文档"], key="rag_mode")

        kb_name = None
        temp_file = None

        if mode == "📁 使用已有知识库":
            kbs = list_knowledge_bases()
            if kbs:
                kb_options = [kb["name"] for kb in kbs]
                kb_name = st.selectbox("选择知识库", kb_options, key="rag_kb_select")
                st.caption(f"已选知识库包含 {next((kb['count'] for kb in kbs if kb['name'] == kb_name), 0)} 个文档块")
            else:
                st.warning("暂无知识库，请先到知识库管理页面创建并上传文档。")
        else:
            temp_file = st.file_uploader("上传文档", type=["pdf", "txt", "docx", "md", "csv", "xlsx"],
                                        key="rag_temp_upload")

        # 模板选择
        rag_templates = get_templates("RAG文档问答")
        template_name = st.selectbox("提示词模板", list(rag_templates.keys()),
                                    format_func=lambda x: rag_templates[x]["name"],
                                    key="rag_template")

        k_value = st.slider("检索文档数", 1, 10, 5, key="rag_k")

        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state["rag_messages"] = []
            st.rerun()

    # ---- 主聊天区域 ----
    # 显示聊天历史
    for msg in st.session_state["rag_messages"]:
        render_chat_message(msg["role"], msg["content"])
        if msg.get("sources"):
            render_sources(msg["sources"])

    # 输入区域
    st.markdown("---")
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input("输入你的问题...", key="rag_input",
                                   placeholder="请输入你想询问的问题，例如：文档的主要内容是什么？")

    with col2:
        send = st.button("📤 发送", use_container_width=True, key="rag_send")

    if send and user_input:
        st.session_state["rag_messages"].append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            if mode == "📁 使用已有知识库" and kb_name:
                for token in rag_query(kb_name, user_input, k=k_value, template_name=template_name):
                    full_response += token
                    placeholder.markdown(full_response + "▌")
            elif mode == "📄 临时上传文档" and temp_file:
                # 保存临时文件
                ext = Path(temp_file.name).suffix
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                    f.write(temp_file.getvalue())
                    tmp_path = f.name
                try:
                    for token in rag_query_temp_file(tmp_path, temp_file.name, user_input, k=k_value):
                        full_response += token
                        placeholder.markdown(full_response + "▌")
                finally:
                    os.unlink(tmp_path)
            else:
                full_response = "请先选择知识库或上传文档。"
                placeholder.markdown(full_response)

            placeholder.markdown(full_response)

        # 保存助手回复及来源
        sources = st.session_state.get("last_sources", [])
        st.session_state["rag_messages"].append({
            "role": "assistant",
            "content": full_response,
            "sources": sources,
        })
        st.rerun()


if __name__ == "__main__":
    main()
