"""
音频生文（ASR）页面 - 语音转文字
"""
import streamlit as st

st.set_page_config(page_title="音频生文", page_icon="🎙️", layout="wide")

from utils.ui_components import inject_css, render_sidebar
from utils.config import init_config
from utils.prompts import init_prompts
from utils.api_client import speech_to_text


def format_timestamp(ms: int) -> str:
    """将毫秒格式化为 HH:MM:SS.mmm"""
    seconds = ms / 1000
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:06.3f}"
    return f"{m:02d}:{s:06.3f}"


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## 🎙️ 音频生文（ASR）")
    st.markdown("*上传音频文件，AI 自动转录为文字，支持中英混合识别与时间戳*")
    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 🎵 音频上传")

        uploaded = st.file_uploader("上传音频文件", type=["wav", "mp3", "flac", "m4a", "ogg"],
                                   key="asr_upload")

        if uploaded:
            st.audio(uploaded.getvalue(), format=f"audio/{uploaded.type.split('/')[-1]}")

            st.markdown("### ⚙️ 识别设置")

            language = st.selectbox("识别语言", [
                ("zh-cn", "中文"),
                ("en", "英文"),
                ("zh-en", "中英混合"),
            ], format_func=lambda x: x[1], key="asr_lang")

            show_words = st.checkbox("显示词级时间戳", key="asr_words")

            transcribe_btn = st.button("🎙️ 开始转录", type="primary", use_container_width=True,
                                      key="asr_transcribe")

    with col_right:
        st.markdown("### 📝 转录结果")

        if uploaded and transcribe_btn:
            # 确定音频格式
            ext = uploaded.name.split(".")[-1].lower()
            fmt_map = {"wav": "wav", "mp3": "mp3", "flac": "flac", "m4a": "mp4", "ogg": "ogg"}
            audio_format = fmt_map.get(ext, "mp3")

            lang_code = dict(language)[0] if isinstance(language, tuple) else language[0]

            with st.spinner("正在识别语音..."):
                text, segments, error = speech_to_text(
                    uploaded.getvalue(),
                    audio_format=audio_format,
                    language=lang_code,
                )

            if error:
                st.error(error)
                st.info("💡 提示：请确认火山引擎 API Key 已正确配置，且已开通语音识别服务。")
            else:
                st.success("转录完成！")

                # 完整文本
                st.markdown("#### 📄 完整文本")
                st.markdown(f"""
                <div style="background:#F8F9FA; padding:16px; border-radius:12px; border:1px solid #E8EAED;">
                {text or '未识别到文字内容'}
                </div>
                """, unsafe_allow_html=True)

                # 带时间戳的句子片段
                if segments:
                    st.markdown("#### ⏱️ 句级时间戳")
                    for i, seg in enumerate(segments, 1):
                        start = seg.get("start_time", seg.get("begin_time", 0))
                        end = seg.get("end_time", 0)
                        seg_text = seg.get("text", "")

                        st.markdown(f"""
                        <div style="display:flex; gap:12px; padding:8px 0; border-bottom:1px solid #F0F0F0;">
                            <span style="color:#4285F4; font-family:monospace; white-space:nowrap;">
                                {format_timestamp(start)} → {format_timestamp(end)}
                            </span>
                            <span>{seg_text}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        # 词级时间戳
                        if show_words and seg.get("words"):
                            word_html = ""
                            for w in seg["words"]:
                                w_start = w.get("start_time", w.get("begin_time", 0))
                                w_end = w.get("end_time", 0)
                                w_text = w.get("text", "")
                                word_html += f'<span title="{format_timestamp(w_start)}-{format_timestamp(w_end)}" style="border-bottom:1px dashed #999; cursor:help;">{w_text}</span> '
                            st.markdown(f'<div style="padding-left:24px; font-size:13px; color:#666;">{word_html}</div>',
                                       unsafe_allow_html=True)

                # 导出选项
                st.markdown("#### 💾 导出")
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.download_button("📝 导出 TXT", text or "",
                                      file_name="transcript.txt", mime="text/plain")
                with col_e2:
                    # 生成 SRT 字幕格式
                    srt_content = ""
                    for i, seg in enumerate(segments or [], 1):
                        start = seg.get("start_time", seg.get("begin_time", 0))
                        end = seg.get("end_time", 0)
                        seg_text = seg.get("text", "")

                        def to_srt(ms):
                            s = ms // 1000
                            h = s // 3600
                            m = (s % 3600) // 60
                            sec = s % 60
                            ms_rem = ms % 1000
                            return f"{h:02d}:{m:02d}:{sec:02d},{ms_rem:03d}"

                        srt_content += f"{i}\n{to_srt(start)} --> {to_srt(end)}\n{seg_text}\n\n"

                    st.download_button("🎬 导出 SRT", srt_content,
                                      file_name="transcript.srt", mime="text/plain")
        elif not uploaded:
            st.info("👈 在左侧上传音频文件并设置参数，点击转录按钮")

    # 使用技巧
    with st.expander("💡 使用技巧"):
        st.markdown("""
        **最佳识别效果建议：**
        1. **音频质量** - 清晰、无背景噪音的音频识别效果最佳
        2. **语言选择** - 纯中文选「中文」，纯英文选「英文」，混合内容选「中英混合」
        3. **文件格式** - WAV 格式保真度最高，MP3 最通用
        4. **时间戳** - 句级时间戳用于字幕制作，词级时间戳用于精细对齐

        **支持的格式：** WAV、MP3、FLAC、M4A、OGG
        """)


if __name__ == "__main__":
    main()
