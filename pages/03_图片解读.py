"""
图片解读页面 - 使用火山引擎豆包视觉模型
"""
import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="图片解读", page_icon="🖼️", layout="wide")

from utils.ui_components import inject_css, render_sidebar
from utils.config import init_config
from utils.prompts import init_prompts, get_templates, get_template, apply_template
from utils.api_client import call_vision_stream


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## 🖼️ 图片解读")
    st.markdown("*AI 视觉分析图像，支持详细描述、构图分析、OCR 文字提取、情感分析等*")
    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📷 图片输入")

        input_mode = st.radio("输入方式", ["📁 本地上传", "🔗 图片URL"], key="vision_input_mode")

        image_data = None
        mime_type = "image/jpeg"

        if input_mode == "📁 本地上传":
            uploaded = st.file_uploader("上传图片", type=["jpg", "jpeg", "png", "webp", "gif", "bmp"],
                                       key="vision_upload")
            if uploaded:
                image_data = uploaded.getvalue()
                mime_type = f"image/{uploaded.type.split('/')[-1]}"
                st.image(image_data, use_column_width=True, caption="已上传图片")
        else:
            url = st.text_input("图片 URL", placeholder="https://example.com/image.jpg", key="vision_url")
            if url:
                try:
                    import requests as req
                    resp = req.get(url, timeout=30)
                    image_data = resp.content
                    mime_type = resp.headers.get("content-type", "image/jpeg")
                    st.image(image_data, use_column_width=True, caption="URL 图片")
                except Exception as e:
                    st.error(f"加载图片失败: {e}")

        # 分析模板
        st.markdown("### 📋 分析模板")
        vision_templates = get_templates("图片解读")
        template_name = st.radio(
            "选择分析方式",
            list(vision_templates.keys()),
            format_func=lambda x: vision_templates[x]["name"],
            key="vision_template",
        )

        # 自由提问的自定义问题
        custom_question = ""
        tmpl = get_template(template_name)
        if tmpl and "自由提问" in tmpl.get("name", ""):
            custom_question = st.text_area("输入你的问题", placeholder="你想了解这张图片的什么？",
                                          key="vision_custom_q")

        analyze_btn = st.button("🔍 开始分析", type="primary", use_container_width=True,
                               key="vision_analyze")

    with col_right:
        st.markdown("### 📝 分析结果")

        if analyze_btn and image_data:
            # 构建提示词
            if custom_question:
                prompt = custom_question
            else:
                prompt = apply_template(template_name)

            with st.spinner("AI 正在分析图片..."):
                result_placeholder = st.empty()
                full_response = ""

                for token in call_vision_stream(image_data, prompt, mime_type=mime_type):
                    full_response += token
                    result_placeholder.markdown(full_response + "▌")

                result_placeholder.markdown(full_response)

            # 保存到历史记录
            if "vision_history" not in st.session_state:
                st.session_state["vision_history"] = []
            st.session_state["vision_history"].append({
                "template": template_name,
                "response": full_response,
            })

            # 下载结果
            st.download_button("💾 下载分析结果", full_response,
                              file_name="image_analysis.txt", mime="text/plain")

        elif analyze_btn and not image_data:
            st.warning("请先上传图片或输入图片 URL。")
        else:
            st.info("👈 在左侧上传图片并选择分析模板，点击分析按钮查看结果")

    # 分析历史记录
    if st.session_state.get("vision_history"):
        with st.expander(f"📜 历史记录 ({len(st.session_state['vision_history'])})"):
            for i, item in enumerate(reversed(st.session_state["vision_history"])):
                st.markdown(f"**{item['template']}**")
                st.markdown(item["response"][:300] + "..." if len(item["response"]) > 300 else item["response"])
                if i < len(st.session_state["vision_history"]) - 1:
                    st.markdown("---")


if __name__ == "__main__":
    main()
