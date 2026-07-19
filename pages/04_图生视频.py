"""
图生视频页面 - 将静态图片转换为动态视频
"""
import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="图生视频", page_icon="🎬", layout="wide")

from utils.ui_components import inject_css, render_sidebar
from utils.config import init_config, get_config
from utils.prompts import init_prompts


def generate_video_from_image(image_data: bytes, motion: str, duration: int,
                              mime_type: str = "image/jpeg"):
    """
    使用火山引擎 Ark 从静态图片生成视频。
    返回 (视频URL, 错误) 元组。
    """
    cfg = get_config("volcengine")
    if not cfg.get("api_key"):
        return None, "请先在系统设置中配置火山引擎 API Key"

    import base64
    b64 = base64.b64encode(image_data).decode("utf-8")
    data_uri = f"data:{mime_type};base64,{b64}"

    # 运动提示词映射
    motion_prompts = {
        "平移左→右": "camera panning from left to right, smooth horizontal movement",
        "平移右→左": "camera panning from right to left, smooth horizontal movement",
        "缩放放大": "camera slowly zooming in, smooth scale up",
        "缩放缩小": "camera slowly zooming out, smooth scale down",
        "上移": "camera tilting upward, smooth vertical pan up",
        "下移": "camera tilting downward, smooth vertical pan down",
    }

    motion_desc = motion_prompts.get(motion, motion)

    try:
        import httpx
        resp = httpx.post(
            f"{cfg['base_url']}/videos/generations",
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "doubao-seedance-1-0-pro-250528",
                "input_image": data_uri,
                "prompt": motion_desc,
                "duration": duration,
            },
            timeout=180,
        )

        if resp.status_code == 200:
            data = resp.json()
            video_url = data.get("data", [{}])[0].get("url", "")
            if video_url:
                return video_url, None
        return None, f"视频生成 API 返回错误: HTTP {resp.status_code}, {resp.text[:200]}"
    except Exception as e:
        return None, f"图生视频调用失败: {str(e)}"


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## 🎬 图生视频")
    st.markdown("*上传静态图片，AI 自动生成动态效果视频*")
    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📷 上传图片")

        uploaded = st.file_uploader("选择一张静态图片", type=["jpg", "jpeg", "png", "webp"],
                                   key="vid_upload")

        if uploaded:
            image_data = uploaded.getvalue()
            st.image(image_data, use_column_width=True, caption="原始图片")

            mime_type = f"image/{uploaded.type.split('/')[-1]}"

            st.markdown("### 🎥 视频参数")

            motion = st.selectbox("运动模板", [
                "平移左→右", "平移右→左", "缩放放大", "缩放缩小", "上移", "下移",
            ], key="vid_motion")

            duration = st.slider("视频时长（秒）", 2, 8, 4, key="vid_duration")

            generate_btn = st.button("🎬 生成视频", type="primary", use_container_width=True,
                                    key="vid_generate")

    with col_right:
        st.markdown("### 🎥 生成结果")

        if uploaded and generate_btn:
            with st.spinner(f"AI 正在生成视频（{duration}秒运动视频，预计需要 30-90 秒）..."):
                st.info(f"运动效果: {motion}，目标时长: {duration}秒")
                video_url, error = generate_video_from_image(
                    uploaded.getvalue(), motion, duration, mime_type,
                )

            if error:
                st.error(error)
                st.info("💡 提示：请确认火山引擎 API Key 已正确配置，且账号已开通视频生成模型权限。")
            elif video_url:
                st.success("视频生成成功！")
                st.video(video_url)

                # 下载按钮
                try:
                    import requests as req
                    resp = req.get(video_url, timeout=60)
                    st.download_button("💾 下载视频", data=resp.content,
                                      file_name="generated_video.mp4",
                                      mime="video/mp4")
                except Exception as e:
                    st.error(f"下载失败: {e}")
            else:
                st.warning("未生成视频，请稍后重试。")
        elif not uploaded:
            st.info("👈 在左侧上传图片并设置参数，点击生成按钮")

    # 使用技巧
    with st.expander("💡 使用技巧"):
        st.markdown("""
        **最佳实践：**
        1. **图片选择** - 选择横向构图的图片效果最佳（16:9 或 4:3）
        2. **画面内容** - 风景、城市场景、自然景观的动画效果更自然
        3. **运动选择** - 水平平移适合风景，缩放适合建筑或静物
        4. **时长控制** - 2-4 秒适合短视频，5-8 秒适合展示类内容

        **支持的格式：** JPG、PNG、WEBP
        """)


if __name__ == "__main__":
    main()
