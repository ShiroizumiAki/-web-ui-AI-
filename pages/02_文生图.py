"""
文生图页面 - 使用火山引擎 Seedream 模型
"""
import streamlit as st
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="文生图", page_icon="🎨", layout="wide")

from utils.ui_components import inject_css, render_sidebar
from utils.config import init_config
from utils.prompts import init_prompts, get_templates, get_template, apply_template
from utils.api_client import generate_image


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## 🎨 文生图")
    st.markdown("*使用火山引擎 Seedream 模型，将文字描述转化为精美图像*")
    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📝 创作配置")

        # 提示词模板
        img_templates = get_templates("文生图")
        template_name = st.selectbox(
            "提示词模板",
            list(img_templates.keys()),
            format_func=lambda x: img_templates[x]["name"],
            key="txt2img_template",
        )

        # 主提示词
        prompt = st.text_area("画面描述 *", height=100,
                             placeholder="描述你想要的画面，例如：一只可爱的橘猫坐在窗台上看夕阳，温暖的阳光洒在它的毛发上...",
                             key="txt2img_prompt")

        # 风格预设
        style = st.selectbox("风格预设", [
            "", "写实摄影", "卡通动漫", "油画", "水彩", "赛博朋克", "中国风", "素描", "3D渲染",
        ], key="txt2img_style")

        # 负面提示词
        negative_prompt = st.text_input("负面提示词（可选）",
                                       placeholder="不想出现的内容，如：模糊、变形、多余的手指",
                                       key="txt2img_negative")

        # 尺寸选择
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            size = st.selectbox("画面尺寸", [
                "1024x1024", "720x1280", "1280x720",
            ], format_func=lambda x: {"1024x1024": "1:1 正方形", "720x1280": "9:16 竖版", "1280x720": "16:9 横版"}[x],
            key="txt2img_size")
        with col_s2:
            num_images = st.selectbox("生成数量", [1, 2, 3, 4], key="txt2img_count")

        generate_btn = st.button("🎨 生成图像", type="primary", use_container_width=True,
                                key="txt2img_generate")

        # 从模板构建最终提示词
        final_prompt = prompt
        if template_name and prompt:
            tmpl = get_template(template_name)
            if tmpl:
                final_prompt = apply_template(template_name, {"prompt": prompt})

    with col_right:
        st.markdown("### 🖼️ 生成结果")

        if generate_btn and prompt:
            with st.spinner("AI 正在创作中，请稍候..."):
                urls, error = generate_image(
                    prompt=final_prompt,
                    size=size,
                    n=num_images,
                    negative_prompt=negative_prompt,
                    style=style,
                )

            if error:
                st.error(error)
                st.info("💡 提示：请确认火山引擎 API Key 已正确配置，且账号已开通 Seedream 模型权限。")
            elif urls:
                st.success(f"成功生成 {len(urls)} 张图像！")

                # 以网格形式展示图片
                n_cols = min(num_images, 2)
                rows = (len(urls) + n_cols - 1) // n_cols

                for row in range(rows):
                    cols = st.columns(n_cols)
                    for col_idx in range(n_cols):
                        idx = row * n_cols + col_idx
                        if idx < len(urls):
                            with cols[col_idx]:
                                try:
                                    resp = requests.get(urls[idx], timeout=30)
                                    img = Image.open(BytesIO(resp.content))
                                    st.image(img, use_column_width=True,
                                            caption=f"生成结果 {idx + 1}")

                                    # 下载按钮
                                    buf = BytesIO()
                                    img.save(buf, format="PNG")
                                    st.download_button(
                                        f"💾 下载图片 {idx + 1}",
                                        data=buf.getvalue(),
                                        file_name=f"generated_{idx + 1}.png",
                                        mime="image/png",
                                        key=f"dl_{idx}",
                                    )
                                except Exception as e:
                                    st.error(f"加载图片失败: {e}")
            else:
                st.warning("未生成图像，请检查 API 配置。")
        elif generate_btn and not prompt:
            st.warning("请输入画面描述。")
        else:
            st.info("👈 在左侧输入画面描述并点击生成按钮")

    # ---- 使用技巧 ----
    with st.expander("💡 提示词技巧"):
        st.markdown("""
        **好的提示词要素：**
        1. **主体描述** - 明确画面的核心内容（人物、物体、场景）
        2. **风格指定** - 如写实、卡通、油画、赛博朋克等
        3. **细节补充** - 光线、色彩、构图、氛围
        4. **画质要求** - 高清、细节丰富、专业级

        **示例提示词：**
        > 一只橘猫坐在窗台上，窗外是夕阳和城市天际线，温暖的阳光洒在猫的毛发上，浅景深，专业摄影，8K超清

        **负面提示词用于排除不想要的元素：**
        > 模糊、变形、多余的手指、低质量、文字、水印
        """)


if __name__ == "__main__":
    main()
