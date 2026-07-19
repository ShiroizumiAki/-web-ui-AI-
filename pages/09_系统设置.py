"""
系统设置页面 - API配置 + 提示词模板管理
"""
import streamlit as st

st.set_page_config(page_title="系统设置", page_icon="⚙️", layout="wide")

from utils.ui_components import inject_css, render_sidebar
from utils.config import (
    init_config, get_config, set_config, is_api_configured, DEFAULTS,
    get_custom_providers, add_custom_provider, delete_custom_provider,
)
from utils.prompts import (
    init_prompts, get_templates, get_template, add_template,
    delete_template, reset_to_defaults, BUILTIN_TEMPLATES,
)


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## ⚙️ 系统设置")
    st.markdown("*管理 API 配置、提示词模板等系统参数*")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔑 API 配置", "📝 提示词模板"])

    # ---- 标签页 1: API 配置 ----
    with tab1:
        st.markdown("### 🔑 API 配置")

        # DeepSeek 配置
        st.markdown("#### 🤖 DeepSeek API")
        ds_cfg = get_config("deepseek")

        col_d1, col_d2 = st.columns([3, 1])
        with col_d1:
            ds_key = st.text_input("API Key", value=ds_cfg.get("api_key", ""),
                                  type="password", key="cfg_ds_key",
                                  placeholder="sk-...")
        with col_d2:
            ds_status = "✅ 已配置" if is_api_configured("deepseek") else "⚠️ 未配置"
            st.markdown(f"<br><span style='font-size:13px;'>{ds_status}</span>",
                       unsafe_allow_html=True)

        col_d3, col_d4 = st.columns(2)
        with col_d3:
            ds_url = st.text_input("Base URL", value=ds_cfg.get("base_url", ""),
                                  key="cfg_ds_url")
        with col_d4:
            ds_model = st.text_input("模型", value=ds_cfg.get("model", ""),
                                    key="cfg_ds_model",
                                    placeholder="deepseek-chat")

        if st.button("💾 保存 DeepSeek 配置", key="save_ds"):
            set_config("deepseek", "api_key", ds_key)
            set_config("deepseek", "base_url", ds_url)
            set_config("deepseek", "model", ds_model)
            st.success("DeepSeek 配置已保存！")

        st.markdown("---")

        # 火山引擎配置
        st.markdown("#### 🌋 火山引擎 API")
        ve_cfg = get_config("volcengine")

        col_v1, col_v2 = st.columns([3, 1])
        with col_v1:
            ve_key = st.text_input("API Key", value=ve_cfg.get("api_key", ""),
                                  type="password", key="cfg_ve_key")
        with col_v2:
            ve_status = "✅ 已配置" if is_api_configured("volcengine") else "⚠️ 未配置"
            st.markdown(f"<br><span style='font-size:13px;'>{ve_status}</span>",
                       unsafe_allow_html=True)

        col_v3, col_v4 = st.columns(2)
        with col_v3:
            ve_url = st.text_input("Base URL", value=ve_cfg.get("base_url", ""),
                                  key="cfg_ve_url")
        with col_v4:
            ve_model = st.text_input("视觉模型", value=ve_cfg.get("vision_model", ""),
                                    key="cfg_ve_model")

        if st.button("💾 保存火山引擎配置", key="save_ve"):
            set_config("volcengine", "api_key", ve_key)
            set_config("volcengine", "base_url", ve_url)
            set_config("volcengine", "vision_model", ve_model)
            st.success("火山引擎配置已保存！")

        st.markdown("---")

        # ---- 自定义 LLM 提供商 ----
        st.markdown("#### 🔧 自定义 LLM 提供商")

        custom_providers = get_custom_providers()

        # 显示已有的自定义提供商
        for name, cp_cfg in list(custom_providers.items()):
            with st.expander(f"🔧 {name} | 模型: {cp_cfg.get('model', 'N/A')}", expanded=False):
                st.caption(f"Base URL: {cp_cfg.get('base_url', '')}")
                key_suffix = cp_cfg.get('api_key', '')
                masked_key = f"***{key_suffix[-4:]}" if key_suffix else "未设置"
                st.caption(f"API Key: {masked_key}")
                if st.button(f"🗑️ 删除 {name}", key=f"del_cp_{name}"):
                    delete_custom_provider(name)
                    st.success(f"自定义提供商「{name}」已删除")
                    st.rerun()

        # 添加新提供商按钮
        if st.button("➕ 添加自定义提供商", key="show_add_cp"):
            st.session_state["show_add_cp_form"] = True

        if st.session_state.get("show_add_cp_form", False):
            st.markdown("**新建自定义提供商**")
            cp_name = st.text_input("提供商名称", key="cp_name",
                                    placeholder="例如: OpenAI, 本地模型...")
            cp_key = st.text_input("API Key", type="password", key="cp_key",
                                   placeholder="sk-...")
            cp_url = st.text_input("Base URL", key="cp_url",
                                   placeholder="https://api.openai.com/v1")
            cp_model = st.text_input("模型名称", key="cp_model",
                                     placeholder="gpt-4o")

            col_cp1, col_cp2 = st.columns(2)
            with col_cp1:
                if st.button("💾 保存", key="save_cp"):
                    if cp_name and cp_url and cp_model:
                        add_custom_provider(cp_name, cp_key, cp_url, cp_model)
                        st.session_state["show_add_cp_form"] = False
                        st.success(f"自定义提供商「{cp_name}」已保存！")
                        st.rerun()
                    else:
                        st.warning("请填写提供商名称、Base URL 和模型名称。")
            with col_cp2:
                if st.button("❌ 取消", key="cancel_cp"):
                    st.session_state["show_add_cp_form"] = False
                    st.rerun()

        st.markdown("---")

        # 重置
        with st.expander("🔄 重置配置"):
            st.warning("将恢复为默认配置（包括内置的示例 API Key）")
            if st.button("重置所有配置", key="reset_all_cfg"):
                for platform in ["deepseek", "volcengine"]:
                    for key, val in DEFAULTS[platform].items():
                        set_config(platform, key, val)
                st.session_state["custom_providers"] = {}
                st.success("配置已重置为默认值")
                st.rerun()

    # ---- 标签页 2: 提示词模板 ----
    with tab2:
        st.markdown("### 📝 提示词模板管理")

        all_templates = get_templates()
        categories = list(set(t["category"] for t in all_templates.values()))

        for category in categories:
            st.markdown(f"#### 📂 {category}")
            cat_templates = {k: v for k, v in all_templates.items()
                           if v.get("category") == category}

            for name, tmpl in cat_templates.items():
                with st.expander(f"{'🔒' if tmpl.get('is_builtin') else '✏️'} {tmpl['name']}", expanded=False):
                    st.caption(f"**ID:** `{name}` | **变量:** {', '.join(tmpl.get('variables', []))}")

                    new_content = st.text_area(
                        "模板内容", value=tmpl["template"], height=200,
                        key=f"tmpl_content_{name}",
                        disabled=tmpl.get("is_builtin"),
                    )

                    if not tmpl.get("is_builtin"):
                        col_t1, col_t2 = st.columns(2)
                        with col_t1:
                            if st.button("💾 保存修改", key=f"save_tmpl_{name}"):
                                tmpl["template"] = new_content
                                add_template(name, tmpl)
                                st.success("模板已更新！")
                                st.rerun()
                        with col_t2:
                            if st.button("🗑️ 删除模板", key=f"del_tmpl_{name}"):
                                delete_template(name)
                                st.success(f"模板「{tmpl['name']}」已删除")
                                st.rerun()

        st.markdown("---")

        # 创建自定义模板
        st.markdown("#### ➕ 创建自定义模板")
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            new_tmpl_name = st.text_input("模板名称", key="new_tmpl_name")
        with col_n2:
            new_tmpl_category = st.selectbox("所属分类", categories + ["自定义"],
                                            key="new_tmpl_category")

        new_tmpl_id = st.text_input("模板 ID（英文标识）", key="new_tmpl_id",
                                   placeholder="my_custom_template")
        new_tmpl_content = st.text_area("模板内容", height=150, key="new_tmpl_content",
                                       placeholder="使用 {variable} 标记变量位置...")
        new_tmpl_vars = st.text_input("变量列表（逗号分隔）", key="new_tmpl_vars",
                                     placeholder="context, question")

        if st.button("➕ 创建模板", key="create_tmpl"):
            if new_tmpl_id and new_tmpl_name and new_tmpl_content:
                variables = [v.strip() for v in new_tmpl_vars.split(",") if v.strip()]
                add_template(new_tmpl_id, {
                    "name": new_tmpl_name,
                    "category": new_tmpl_category,
                    "template": new_tmpl_content,
                    "variables": variables,
                    "is_builtin": False,
                })
                st.success(f"模板「{new_tmpl_name}」创建成功！")
                st.rerun()
            else:
                st.warning("请填写模板名称、ID 和内容。")

        # 重置所有模板
        st.markdown("---")
        with st.expander("🔄 重置提示词模板"):
            st.warning("将删除所有自定义模板并恢复内置模板。")
            if st.button("重置所有模板", key="reset_tmpl"):
                reset_to_defaults()
                st.success("已恢复为默认模板！")
                st.rerun()


if __name__ == "__main__":
    main()
