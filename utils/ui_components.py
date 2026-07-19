"""
多模态 AI 平台的可复用 UI 组件。
"""
import streamlit as st

from utils.config import init_config, is_api_configured, get_custom_providers
from utils.prompts import init_prompts


# ============================================================
# 全局 CSS
# ============================================================

def inject_css():
    """注入整个应用的自定义 CSS。"""
    st.markdown("""
    <style>
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #FAFBFC;
        border-right: 1px solid #E8EAED;
    }
    [data-testid="stSidebar"] .stMarkdown {
        padding: 0 8px;
    }

    /* 卡片样式 */
    .feature-card {
        background: white;
        border: 1px solid #E8EAED;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transform: translateY(-2px);
        border-color: #4285F4;
    }
    .feature-card .icon {
        font-size: 32px;
        margin-bottom: 12px;
    }
    .feature-card .title {
        font-size: 16px;
        font-weight: 600;
        color: #202124;
        margin-bottom: 8px;
    }
    .feature-card .desc {
        font-size: 13px;
        color: #5F6368;
        line-height: 1.5;
        margin-bottom: 16px;
    }

    /* 顶部横幅 */
    .hero-banner {
        background: linear-gradient(135deg, #4285F4 0%, #1A73E8 50%, #0D47A1 100%);
        border-radius: 24px;
        padding: 40px 48px;
        margin-bottom: 32px;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .hero-banner .title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .hero-banner .subtitle {
        font-size: 15px;
        opacity: 0.9;
        margin-bottom: 20px;
    }
    .hero-banner .quick-links {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    .hero-banner .quick-link {
        background: rgba(255,255,255,0.18);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        text-decoration: none;
        transition: background 0.2s;
    }
    .hero-banner .quick-link:hover {
        background: rgba(255,255,255,0.30);
    }

    /* 分区标题 */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 32px 0 16px 0;
    }
    .section-header .icon {
        font-size: 22px;
    }
    .section-header .title {
        font-size: 20px;
        font-weight: 700;
        color: #202124;
    }

    /* 步骤卡片 */
    .step-card {
        background: white;
        border: 1px solid #E8EAED;
        border-radius: 16px;
        padding: 28px 24px;
        text-align: center;
        height: 100%;
    }
    .step-card .step-num {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 18px;
        color: white;
        margin-bottom: 16px;
    }
    .step-card .step-1 { background: #4285F4; }
    .step-card .step-2 { background: #34A853; }
    .step-card .step-3 { background: #FBBC04; }
    .step-card .title {
        font-size: 16px;
        font-weight: 600;
        color: #202124;
        margin-bottom: 8px;
    }
    .step-card .desc {
        font-size: 13px;
        color: #5F6368;
        line-height: 1.5;
    }

    /* 技术栈卡片 */
    .tech-card {
        background: white;
        border: 1px solid #E8EAED;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        height: 100%;
    }
    .tech-card .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .tech-card .name {
        font-size: 15px;
        font-weight: 600;
        color: #202124;
    }
    .tech-card .detail {
        font-size: 12px;
        color: #5F6368;
        margin-top: 4px;
    }

    .badge-blue { background: #E8F0FE; color: #1A73E8; }
    .badge-purple { background: #F3E8FD; color: #9334E6; }
    .badge-yellow { background: #FEF7E0; color: #E37400; }
    .badge-green { background: #E6F4EA; color: #1E8E3E; }
    .badge-pink { background: #FCE8E6; color: #D93025; }
    .badge-cyan { background: #E0F7FA; color: #00838F; }

    /* API 状态 */
    .api-status-ok {
        background: #E6F4EA;
        color: #1E8E3E;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .api-status-error {
        background: #FCE8E6;
        color: #D93025;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* 聊天样式 */
    .chat-message {
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    .chat-user {
        background: #E8F0FE;
        color: #202124;
    }
    .chat-assistant {
        background: #F8F9FA;
        border: 1px solid #E8EAED;
    }
    .chat-sources {
        background: #FFF8E1;
        border-left: 3px solid #FBBC04;
        padding: 10px 14px;
        border-radius: 6px;
        margin-top: 10px;
        font-size: 12px;
    }

    /* 按钮 */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s;
    }

    /* 单选按钮组卡片化 */
    div[role="radiogroup"] label {
        border: 1px solid #E8EAED;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 4px;
        transition: all 0.2s;
    }
    div[role="radiogroup"] label:hover {
        border-color: #4285F4;
    }

    /* 文件上传器 */
    [data-testid="stFileUploader"] {
        border: 2px dashed #DADCE0;
        border-radius: 16px;
        padding: 20px;
        transition: border-color 0.2s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #4285F4;
    }

    /* 侧边栏首页链接按钮 */
    button[key="home_link"] {
        background: none;
        border: none;
        font-size: 20px;
        font-weight: 700;
        color: #1A73E8;
        text-align: left;
        padding: 4px 0;
        cursor: pointer;
    }
    button[key="home_link"]:hover {
        color: #0D47A1;
    }
    button[key="home_link"]:focus {
        outline: none;
        color: #0D47A1;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 侧边栏导航
# ============================================================

NAV_ITEMS = [
    {"emoji": "📚", "label": "RAG文档问答", "page": "01_RAG文档问答"},
    {"emoji": "🎨", "label": "文生图", "page": "02_文生图"},
    {"emoji": "🖼️", "label": "图片解读", "page": "03_图片解读"},
    {"emoji": "🎬", "label": "图生视频", "page": "04_图生视频"},
    {"emoji": "🔊", "label": "文生音频", "page": "05_文生音频"},
    {"emoji": "🎙️", "label": "音频生文", "page": "06_音频生文"},
    {"emoji": "📊", "label": "Excel助手", "page": "07_Excel助手"},
    {"emoji": "📁", "label": "知识库管理", "page": "08_知识库管理"},
    {"emoji": "⚙️", "label": "系统设置", "page": "09_系统设置"},
]


def render_sidebar():
    """渲染全局侧边栏导航。"""
    init_config()
    init_prompts()

    with st.sidebar:
        if st.button("🤖 多模态AI助手", key="home_link", use_container_width=True):
            st.switch_page("app.py")
        st.markdown("---")

        # 导航菜单项
        for item in NAV_ITEMS:
            st.page_link(f"pages/{item['page']}.py",
                         icon=item["emoji"])

        st.markdown("---")

        # API 状态
        deepseek_ok = is_api_configured("deepseek")
        volcengine_ok = is_api_configured("volcengine")

        # 检查自定义提供商
        custom_providers = get_custom_providers()
        custom_ok = all(
            is_api_configured(config_dict=cfg)
            for cfg in custom_providers.values()
        ) if custom_providers else True

        all_ok = deepseek_ok and volcengine_ok and custom_ok

        if all_ok:
            st.markdown(
                '<div class="api-status-ok">✅ API 已配置</div>',
                unsafe_allow_html=True,
            )
        else:
            missing = []
            if not deepseek_ok:
                missing.append("DeepSeek")
            if not volcengine_ok:
                missing.append("火山引擎")
            for name, cfg in custom_providers.items():
                if not is_api_configured(config_dict=cfg):
                    missing.append(name)
            st.markdown(
                f'<div class="api-status-error">⚠️ 未配置: {", ".join(missing)}</div>',
                unsafe_allow_html=True,
            )

        # 页脚
        st.markdown(
            '<p style="font-size:12px; color:#9AA0A6; margin-top:24px;">'
            '请使用上方导航菜单选择功能页面</p>',
            unsafe_allow_html=True,
        )


# ============================================================
# 卡片组件
# ============================================================

def render_feature_card(emoji: str, title: str, description: str,
                        page: str, key: str = None):
    """渲染功能导航卡片。"""
    cols = st.columns([1, 8, 1])
    with cols[1]:
        st.markdown(f"""
        <div class="feature-card">
            <div class="icon">{emoji}</div>
            <div class="title">{title}</div>
            <div class="desc">{description}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("进入 →", key=f"card_{key or title}", use_container_width=True):
            st.switch_page(f"pages/{page}.py")


def render_step_card(step_num: int, step_class: str, title: str, description: str):
    """渲染步骤引导卡片。"""
    st.markdown(f"""
    <div class="step-card">
        <div class="step-num {step_class}">{step_num}</div>
        <div class="title">{title}</div>
        <div class="desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def render_tech_card(badge_text: str, badge_class: str, name: str, detail: str):
    """渲染技术栈信息卡片。"""
    st.markdown(f"""
    <div class="tech-card">
        <div class="badge {badge_class}">{badge_text}</div>
        <div class="name">{name}</div>
        <div class="detail">{detail}</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 聊天消息
# ============================================================

def render_chat_message(role: str, content: str):
    """渲染聊天消息气泡。"""
    css_class = "chat-user" if role == "user" else "chat-assistant"
    icon = "👤" if role == "user" else "🤖"
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <strong>{icon} {'你' if role == 'user' else 'AI助手'}</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def render_sources(sources: list):
    """渲染来源引用信息。"""
    if not sources:
        return
    html = '<div class="chat-sources"><strong>📖 参考来源:</strong><br>'
    for i, doc in enumerate(sources, 1):
        score_pct = int(doc.get("score", 0) * 100)
        html += f'{i}. <strong>{doc["source"]}</strong> (相关度: {score_pct}%)<br>'
        html += f'<em>"{doc["content"][:150]}..."</em><br>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
