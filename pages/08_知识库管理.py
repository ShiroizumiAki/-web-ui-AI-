"""
知识库管理页面 - 创建/删除知识库，上传文档
"""
import streamlit as st
import os
import tempfile
from pathlib import Path

st.set_page_config(page_title="知识库管理", page_icon="📁", layout="wide")

from utils.ui_components import inject_css, render_sidebar
from utils.config import init_config
from utils.prompts import init_prompts
from utils.knowledge_base import (
    create_knowledge_base, delete_knowledge_base, list_knowledge_bases,
    add_documents, get_kb_documents, remove_document, search_knowledge_base,
)


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## 📁 知识库管理")
    st.markdown("*创建知识库、上传私域文档，构建持久化的 RAG 向量知识库*")
    st.markdown("---")

    # ---- 标签页 ----
    tab1, tab2, tab3 = st.tabs(["📚 知识库列表", "📤 上传文档", "🔍 检索测试"])

    # 刷新知识库列表
    kbs = list_knowledge_bases()

    # ---- 标签页 1: 知识库列表 ----
    with tab1:
        st.markdown("### 📚 我的知识库")

        # 创建新知识库
        col_new1, col_new2 = st.columns([3, 1])
        with col_new1:
            new_kb_name = st.text_input("新建知识库名称", placeholder="输入知识库名称...",
                                       key="kb_new_name")
        with col_new2:
            if st.button("➕ 创建", use_container_width=True, key="kb_create_btn"):
                if new_kb_name.strip():
                    ok = create_knowledge_base(new_kb_name.strip())
                    if ok:
                        st.success(f"知识库「{new_kb_name}」创建成功！")
                        st.rerun()
                    else:
                        st.warning(f"知识库「{new_kb_name}」已存在。")
                else:
                    st.warning("请输入知识库名称。")

        st.markdown("---")

        if not kbs:
            st.info("暂无知识库，请在输入框中创建第一个知识库。")
        else:
            for kb in kbs:
                col_k1, col_k2, col_k3 = st.columns([3, 1, 1])
                with col_k1:
                    st.markdown(f"**📁 {kb['name']}**")
                    st.caption(f"{kb['count']} 个文档块")

                    # 显示文档
                    docs = get_kb_documents(kb["name"])
                    if docs:
                        doc_list = "、".join(docs[:5])
                        if len(docs) > 5:
                            doc_list += f" 等 {len(docs)} 个文件"
                        st.caption(f"📄 {doc_list}")

                with col_k2:
                    if st.button("🔍", key=f"search_{kb['name']}", help="检索测试"):
                        st.session_state["kb_test_name"] = kb["name"]
                        # 切换到标签页 3 的逻辑...

                with col_k3:
                    if st.button("🗑️", key=f"del_{kb['name']}", help="删除知识库"):
                        if delete_knowledge_base(kb["name"]):
                            st.success(f"知识库「{kb['name']}」已删除")
                            st.rerun()

                st.markdown("---")

    # ---- 标签页 2: 上传文档 ----
    with tab2:
        st.markdown("### 📤 上传文档")

        if not kbs:
            st.warning("请先在「知识库列表」中创建知识库。")
        else:
            target_kb = st.selectbox("目标知识库", [kb["name"] for kb in kbs],
                                    key="kb_upload_target")

            uploaded_files = st.file_uploader(
                "选择文档（支持多文件）",
                type=["pdf", "txt", "docx", "md", "csv", "xlsx"],
                accept_multiple_files=True,
                key="kb_upload_files",
            )

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                chunk_size = st.number_input("分块大小", 200, 3000, 1000, 100,
                                           key="kb_chunk_size")
            with col_s2:
                chunk_overlap = st.number_input("重叠大小", 0, 500, 200, 50,
                                              key="kb_chunk_overlap")

            if uploaded_files and st.button("📤 上传并处理", type="primary",
                                            key="kb_upload_btn"):
                total_chunks = 0

                for file in uploaded_files:
                    # 保存到临时文件
                    ext = Path(file.name).suffix
                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                        f.write(file.getvalue())
                        tmp_path = f.name

                    try:
                        with st.spinner(f"正在处理: {file.name}..."):
                            progress_bar = st.progress(0)

                            def update_progress(p):
                                progress_bar.progress(p)

                            n = add_documents(
                                target_kb, tmp_path, file.name,
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap,
                                progress_callback=update_progress,
                            )
                            total_chunks += n
                            progress_bar.progress(1.0)

                        st.success(f"✅ {file.name} - 已添加 {n} 个文档块")
                    except Exception as e:
                        st.error(f"❌ {file.name} - 处理失败: {e}")
                    finally:
                        os.unlink(tmp_path)

                if total_chunks > 0:
                    st.success(f"🎉 总计添加 {total_chunks} 个文档块到知识库「{target_kb}」！")
                    st.rerun()

            # 显示已有文档
            st.markdown("---")
            st.markdown("**已有文档:**")
            docs = get_kb_documents(target_kb)
            if docs:
                for doc in docs:
                    col_d1, col_d2 = st.columns([5, 1])
                    with col_d1:
                        st.markdown(f"📄 {doc}")
                    with col_d2:
                        if st.button("🗑️", key=f"rm_{doc}", help="删除此文档"):
                            n = remove_document(target_kb, doc)
                            st.success(f"已删除 {n} 个文档块")
                            st.rerun()
            else:
                st.caption("暂无文档")

    # ---- 标签页 3: 检索测试 ----
    with tab3:
        st.markdown("### 🔍 检索测试")

        if not kbs:
            st.warning("请先创建知识库并上传文档。")
        else:
            search_kb = st.selectbox("选择知识库", [kb["name"] for kb in kbs],
                                    key="kb_search_target",
                                    index=0 if st.session_state.get("kb_test_name") is None
                                    else next((i for i, kb in enumerate(kbs)
                                              if kb["name"] == st.session_state["kb_test_name"]), 0))

            search_query = st.text_input("检索内容", placeholder="输入要检索的文本...",
                                       key="kb_search_query")

            k = st.slider("返回结果数", 1, 10, 5, key="kb_search_k")

            if search_query and st.button("🔍 检索", key="kb_search_btn"):
                results = search_knowledge_base(search_kb, search_query, k=k)

                if not results:
                    st.warning("未找到相关内容。")
                else:
                    for i, doc in enumerate(results, 1):
                        score_pct = int(doc["score"] * 100)
                        st.markdown(f"""
                        <div style="background:white; border:1px solid #E8EAED; border-radius:12px; padding:16px; margin-bottom:12px;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                                <strong>结果 {i}</strong>
                                <span style="color:#4285F4;">相关度: {score_pct}%</span>
                            </div>
                            <div style="color:#5F6368; font-size:13px; margin-bottom:8px;">
                                📄 来源: {doc['source']}
                            </div>
                            <div style="line-height:1.6;">
                                {doc['content']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
