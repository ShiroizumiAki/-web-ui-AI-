"""
提示词模板管理。
提供各功能的内置模板，并支持自定义模板。
"""
import streamlit as st

# 内置提示词模板
BUILTIN_TEMPLATES = {
    "rag_default": {
        "name": "RAG 默认问答",
        "category": "RAG文档问答",
        "template": """你是一个专业的文档问答助手。请根据以下文档内容回答用户的问题。

## 文档内容
{context}

## 用户问题
{question}

## 回答要求
1. 仅基于提供的文档内容回答，不要编造信息
2. 如果文档中没有相关信息，请明确告知用户
3. 回答要准确、简洁、有条理
4. 引用具体的文档片段来支持你的回答""",
        "variables": ["context", "question"],
    },
    "rag_detailed": {
        "name": "RAG 详细分析",
        "category": "RAG文档问答",
        "template": """你是一个严谨的文档分析专家。请仔细阅读以下文档内容，并对用户的问题进行深入分析。

## 参考文档
{context}

## 分析问题
{question}

## 分析框架
请按以下结构组织你的回答：
1. **核心观点**: 文档中与该问题直接相关的核心信息
2. **详细分析**: 对相关内容的深入解读
3. **关键引用**: 引用文档中的关键段落
4. **补充说明**: 相关背景或注意事项
5. **总结**: 一句话总结""",
        "variables": ["context", "question"],
    },
    "image_describe": {
        "name": "详细描述",
        "category": "图片解读",
        "template": """请详细描述这张图片的内容。包括：
1. 整体场景和主题
2. 画面中的主要元素和它们的空间关系
3. 色彩、光线和构图特点
4. 图片传达的氛围或情感
5. 任何值得注意的细节

请用中文回答，描述要全面且有条理。""",
        "variables": [],
    },
    "image_composition": {
        "name": "构图分析",
        "category": "图片解读",
        "template": """请从摄影/绘画的专业角度分析这张图片的构图：
1. 构图方式（三分法、对称、引导线等）
2. 主体与背景的关系
3. 视觉焦点和视线引导
4. 空间层次（前景、中景、背景）
5. 画面平衡感

请用中文回答，适当使用专业术语。""",
        "variables": [],
    },
    "image_ocr": {
        "name": "OCR 文字提取",
        "category": "图片解读",
        "template": """请仔细识别并提取这张图片中的所有文字内容。
- 保持原文的格式和排版顺序
- 如果文字不清晰，标注 [不确定: ...]
- 对于表格或列表，保持结构
- 标注文字在图片中的大致位置（上方/中部/下方等）

请用中文回答。""",
        "variables": [],
    },
    "image_emotion": {
        "name": "情感分析",
        "category": "图片解读",
        "template": """请分析这张图片传达的情感和氛围：
1. 整体情绪基调（如：温暖、冷峻、欢快、忧郁等）
2. 色彩对情绪的影响
3. 人物表情/姿态传达的情感（如有）
4. 场景营造的氛围感
5. 观看者的主观感受

请用中文回答，分析要细腻且有洞察力。""",
        "variables": [],
    },
    "txt2img_default": {
        "name": "文生图默认",
        "category": "文生图",
        "template": """{prompt}，高质量，细节丰富，专业级画面""",
        "variables": ["prompt"],
    },
    "txt2img_photography": {
        "name": "摄影风格",
        "category": "文生图",
        "template": """{prompt}，专业摄影，真实感，自然光线，浅景深，8K超清，RAW格式质感""",
        "variables": ["prompt"],
    },
    "txt2img_illustration": {
        "name": "插画风格",
        "category": "文生图",
        "template": """{prompt}，精美插画风格，柔和色彩，细腻笔触，艺术感""",
        "variables": ["prompt"],
    },
    "excel_analysis": {
        "name": "数据分析洞察",
        "category": "Excel助手",
        "template": """你是一个数据分析专家。以下是数据的基本统计信息：

## 数据概览
- 行数: {rows}
- 列数: {columns}
- 列名: {col_names}

## 描述性统计
{describe}

请提供：
1. 数据质量评估（缺失值、异常值等）
2. 关键发现和趋势
3. 值得进一步分析的维度
4. 业务建议（如果适用）

请用中文回答。""",
        "variables": ["rows", "columns", "col_names", "describe"],
    },
}


def init_prompts():
    """在 session state 中初始化提示词模板。"""
    if "prompt_templates" not in st.session_state:
        st.session_state["prompt_templates"] = {
            name: {**tmpl, "is_builtin": True}
            for name, tmpl in BUILTIN_TEMPLATES.items()
        }


def get_templates(category: str = None) -> dict:
    """获取所有模板，可按分类筛选。"""
    init_prompts()
    templates = st.session_state["prompt_templates"]
    if category:
        return {k: v for k, v in templates.items() if v.get("category") == category}
    return templates


def get_template(name: str) -> dict:
    """按名称获取指定模板。"""
    init_prompts()
    return st.session_state["prompt_templates"].get(name)


def add_template(name: str, template_data: dict):
    """添加或更新自定义模板。"""
    init_prompts()
    template_data["is_builtin"] = False
    st.session_state["prompt_templates"][name] = template_data


def delete_template(name: str):
    """删除自定义模板（不可删除内置模板）。"""
    init_prompts()
    tmpl = st.session_state["prompt_templates"].get(name)
    if tmpl and not tmpl.get("is_builtin"):
        del st.session_state["prompt_templates"][name]


def reset_to_defaults():
    """将所有模板重置为内置默认值。"""
    st.session_state["prompt_templates"] = {
        name: {**tmpl, "is_builtin": True}
        for name, tmpl in BUILTIN_TEMPLATES.items()
    }


def apply_template(name: str, variables: dict = None) -> str:
    """用变量填充模板。"""
    tmpl = get_template(name)
    if not tmpl:
        return ""
    text = tmpl["template"]
    if variables:
        for var, val in variables.items():
            text = text.replace("{" + var + "}", str(val))
    return text
