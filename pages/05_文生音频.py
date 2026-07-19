"""
文生音频（TTS）页面 - 文本转语音
"""
import streamlit as st

st.set_page_config(page_title="文生音频", page_icon="🔊", layout="wide")

from utils.ui_components import inject_css, render_sidebar
from utils.config import init_config
from utils.prompts import init_prompts
from utils.api_client import text_to_speech, VOICE_OPTIONS


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## 🔊 文生音频（TTS）")
    st.markdown("*将文字转换为自然流畅的语音，支持 6 种音色、语速和音量调节*")
    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 📝 文本输入")

        text = st.text_area("输入要转换为语音的文字 *", height=200,
                           placeholder="请输入要转换为语音的文字内容...\n\n支持长文本，系统会自动分段处理。",
                           key="tts_text")

        char_count = len(text)
        st.caption(f"已输入 {char_count} 个字符")

        st.markdown("---")
        st.markdown("### 🎤 语音设置")

        # 音色选择（卡片展示）
        voice_names = list(VOICE_OPTIONS.keys())
        voice_descriptions = {
            "温柔女声": "柔和温暖，适合叙事",
            "活泼女声": "明亮欢快，适合播音",
            "知性女声": "沉稳专业，适合讲解",
            "沉稳男声": "深沉厚重，适合播报",
            "阳光男声": "清爽自然，适合对话",
            "磁性男声": "富有感染力，适合朗读",
        }

        # 以选择框形式显示音色选项
        voice = st.selectbox("选择音色", voice_names,
                            format_func=lambda x: f"{x} - {voice_descriptions.get(x, '')}",
                            key="tts_voice")

        # 语速和音量
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1, key="tts_speed",
                             help="0.5x = 半速, 1.0x = 正常, 2.0x = 两倍速")
        with col_v2:
            volume = st.slider("音量", 0.1, 2.0, 1.0, 0.1, key="tts_volume",
                              help="1.0 = 正常音量")

        generate_btn = st.button("🔊 生成语音", type="primary", use_container_width=True,
                                key="tts_generate")

    with col_right:
        st.markdown("### 🎧 语音播放")

        if generate_btn and text.strip():
            with st.spinner("正在合成语音..."):
                audio_bytes, error = text_to_speech(
                    text=text.strip(),
                    voice=voice,
                    speed=speed,
                    volume=volume,
                )

            if error:
                st.error(error)
                st.info("💡 提示：请确认火山引擎 API Key 已正确配置，且已开通语音合成服务。")
            elif audio_bytes:
                st.success("语音合成成功！")
                st.audio(audio_bytes, format="audio/mp3")

                # 下载
                st.download_button("💾 下载音频", data=audio_bytes,
                                  file_name="tts_output.mp3",
                                  mime="audio/mp3")
        elif generate_btn and not text.strip():
            st.warning("请输入要转换的文字内容。")
        else:
            st.info("👈 在左侧输入文字并选择音色参数，点击生成按钮")

    # 音色对比
    with st.expander("🎤 音色试听与对比"):
        st.markdown("""
        **可用音色说明：**

        | 音色 | 风格 | 适用场景 |
        |------|------|----------|
        | 温柔女声 | 柔和温暖 | 有声书、情感故事 |
        | 活泼女声 | 明亮欢快 | 新闻播报、商业配音 |
        | 知性女声 | 沉稳专业 | 课程讲解、知识科普 |
        | 沉稳男声 | 深沉厚重 | 新闻播报、纪录片 |
        | 阳光男声 | 清爽自然 | 对话配音、社交媒体 |
        | 磁性男声 | 富有感染力 | 广告配音、朗读 |

        **语速建议：**
        - 教学/讲解：0.8x - 1.0x
        - 正常朗读：1.0x
        - 新闻播报：1.2x - 1.5x
        """)


if __name__ == "__main__":
    main()
