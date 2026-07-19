"""
Excel 数据助手页面 - 上传表格数据，预览、筛选、排序，生成交互式图表
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="Excel助手", page_icon="📊", layout="wide")

from utils.ui_components import inject_css, render_sidebar
from utils.config import init_config
from utils.prompts import init_prompts
from utils.api_client import call_deepseek


def main():
    inject_css()
    init_config()
    init_prompts()
    render_sidebar()

    st.markdown("## 📊 Excel 数据助手")
    st.markdown("*上传表格数据，支持预览、筛选、排序，生成交互式 Plotly 图表和统计分析*")
    st.markdown("---")

    # 文件上传
    uploaded = st.file_uploader("上传数据文件", type=["csv", "xlsx", "xls"],
                               key="excel_upload")

    if not uploaded:
        st.info("👆 请上传 CSV 或 Excel 文件开始分析")
        with st.expander("📋 示例数据"):
            st.markdown("""
            **支持的功能：**
            - 📋 数据预览（可排序、可筛选）
            - 📊 多种交互式图表（柱状图、折线图、散点图、饼图、箱线图、热力图）
            - 📈 描述性统计分析
            - 🤖 AI 数据洞察（调用 DeepSeek 分析）
            - 💾 图表和结果导出
            """)
        return

    # 加载数据
    try:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"文件读取失败: {e}")
        return

    # 存入 session state 以保持状态持久化
    st.session_state["excel_df"] = df

    # ---- 标签页 ----
    tab1, tab2, tab3, tab4 = st.tabs(["📋 数据预览", "📊 可视化图表", "📈 统计分析", "🤖 AI洞察"])

    # ---- 标签页 1: 数据预览 ----
    with tab1:
        st.markdown(f"**数据规模:** {df.shape[0]} 行 × {df.shape[1]} 列")

        # 搜索/筛选
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            search = st.text_input("🔍 全局搜索", placeholder="输入关键词筛选...", key="excel_search")

        # 应用搜索筛选
        display_df = df
        if search:
            mask = display_df.astype(str).apply(
                lambda row: row.str.contains(search, case=False, na=False).any(), axis=1
            )
            display_df = display_df[mask]
            st.caption(f"筛选结果: {display_df.shape[0]} 行")

        # 显示数据表
        st.dataframe(display_df, use_container_width=True, height=400,
                    hide_index=True)

        # 下载筛选后的数据
        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("💾 导出为 CSV", csv, "filtered_data.csv", "text/csv")

    # ---- 标签页 2: 图表 ----
    with tab2:
        st.markdown("### 📊 可视化图表")

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        all_cols = df.columns.tolist()

        if not numeric_cols:
            st.warning("数据中没有数值列，无法生成图表。")
        else:
            chart_type = st.selectbox("图表类型", [
                "柱状图", "折线图", "散点图", "饼图", "箱线图", "热力图",
            ], key="chart_type")

            col_c1, col_c2 = st.columns(2)

            if chart_type == "饼图":
                with col_c1:
                    names_col = st.selectbox("分类列", all_cols, key="pie_names")
                with col_c2:
                    values_col = st.selectbox("数值列", numeric_cols, key="pie_values")

                fig = px.pie(df, names=names_col, values=values_col,
                            title=f"{values_col} 分布（按 {names_col}）")
                fig.update_traces(textposition="inside", textinfo="percent+label")

            elif chart_type == "热力图":
                corr = df[numeric_cols].corr()
                fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                               title="相关性热力图",
                               color_continuous_scale="RdBu_r")

            elif chart_type == "箱线图":
                with col_c1:
                    y_col = st.selectbox("数值列", numeric_cols, key="box_y")
                with col_c2:
                    x_col = st.selectbox("分组列（可选）", ["无"] + all_cols, key="box_x")

                if x_col == "无":
                    fig = px.box(df, y=y_col, title=f"{y_col} 箱线图")
                else:
                    fig = px.box(df, x=x_col, y=y_col, title=f"{y_col} 按 {x_col} 分组")

            else:
                with col_c1:
                    x_col = st.selectbox("X 轴", all_cols, key="chart_x")
                with col_c2:
                    y_col = st.selectbox("Y 轴", numeric_cols, key="chart_y")

                color_col = st.selectbox("颜色分组（可选）", ["无"] + all_cols, key="chart_color")
                color = None if color_col == "无" else color_col

                if chart_type == "柱状图":
                    fig = px.bar(df, x=x_col, y=y_col, color=color,
                                title=f"{y_col} 按 {x_col}")
                elif chart_type == "折线图":
                    fig = px.line(df, x=x_col, y=y_col, color=color,
                                 title=f"{y_col} 趋势")
                elif chart_type == "散点图":
                    fig = px.scatter(df, x=x_col, y=y_col, color=color,
                                    title=f"{x_col} vs {y_col}")

            fig.update_layout(height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    # ---- 标签页 3: 统计分析 ----
    with tab3:
        st.markdown("### 📈 统计分析")

        if numeric_cols:
            st.markdown("#### 描述性统计")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)

            st.markdown("#### 缺失值分析")
            missing = df.isnull().sum()
            missing_pct = (missing / len(df) * 100).round(2)
            missing_df = pd.DataFrame({
                "列名": missing.index,
                "缺失数量": missing.values,
                "缺失比例(%)": missing_pct.values,
            })
            missing_df = missing_df[missing_df["缺失数量"] > 0]
            if missing_df.empty:
                st.success("✅ 数据完整，无缺失值")
            else:
                st.dataframe(missing_df, use_container_width=True)

            st.markdown("#### 相关性矩阵")
            corr = df[numeric_cols].corr()
            st.dataframe(corr.style.background_gradient(cmap="RdBu_r", vmin=-1, vmax=1),
                        use_container_width=True)
        else:
            st.info("数据中没有数值列用于统计分析。")

    # ---- 标签页 4: AI 数据洞察 ----
    with tab4:
        st.markdown("### 🤖 AI 数据洞察")

        if st.button("🔍 生成 AI 洞察", type="primary", key="excel_ai"):
            with st.spinner("DeepSeek 正在分析数据..."):
                # 准备数据摘要
                desc = df.describe(include="all").to_string()
                content, error = call_deepseek([
                    {"role": "system", "content": "你是一个数据分析专家，请基于提供的数据统计信息给出洞察。"},
                    {"role": "user", "content": f"""请分析以下数据并提供洞察：

数据信息：
- 行数: {df.shape[0]}
- 列数: {df.shape[1]}
- 列名: {', '.join(df.columns.tolist())}

描述性统计：
{desc}

请提供：
1. 数据质量评估
2. 关键发现和趋势
3. 值得深入分析的维度
4. 业务建议"""}
                ])

            if error:
                st.error(error)
            else:
                st.markdown(content)

                # 同时允许自定义追问
                st.markdown("---")
                custom_q = st.text_area("追问（可选）", placeholder="针对数据提出更多问题...",
                                       key="excel_followup")

                if custom_q and st.button("📤 追问", key="excel_followup_btn"):
                    with st.spinner("分析中..."):
                        answer, err = call_deepseek([
                            {"role": "system", "content": "你是一个数据分析专家。"},
                            {"role": "user", "content": f"数据概览：\n{desc[:2000]}\n\n问题：{custom_q}"}
                        ])
                    if err:
                        st.error(err)
                    else:
                        st.markdown(answer)


if __name__ == "__main__":
    main()
