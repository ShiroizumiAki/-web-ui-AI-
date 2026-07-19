"""
RAG（检索增强生成）流水线。
"""
import streamlit as st

from utils.api_client import call_deepseek_stream
from utils.config import get_config
from utils.knowledge_base import search_knowledge_base, add_documents, _get_collection
from utils.prompts import get_template, apply_template


def build_rag_prompt(context: str, question: str, template_name: str = "rag_default") -> str:
    """使用模板构建 RAG 提示词。"""
    tmpl = get_template(template_name)
    if tmpl:
        return apply_template(template_name, {"context": context, "question": question})

    # 回退方案
    return f"""你是一个专业的文档问答助手。请根据以下文档内容回答用户的问题。

## 文档内容
{context}

## 用户问题
{question}

## 回答要求
1. 仅基于提供的文档内容回答，不要编造信息
2. 如果文档中没有相关信息，请明确告知用户
3. 回答要准确、简洁、有条理"""


def rag_query(kb_name: str, question: str, k: int = 5,
              template_name: str = "rag_default"):
    """
    对知识库执行 RAG 查询。
    返回一个生成器，逐块产出回答内容。
    """
    if not kb_name:
        yield "请先选择或创建知识库。"
        return

    # 检索知识库
    docs = search_knowledge_base(kb_name, question, k=k)

    if not docs:
        yield "未在知识库中找到相关内容，请尝试换个问题或上传更多文档。"
        return

    # 从检索到的文档构建上下文
    context_parts = []
    for i, doc in enumerate(docs, 1):
        context_parts.append(f"[来源{i}: {doc['source']}]\n{doc['content']}")
    context = "\n\n---\n\n".join(context_parts)

    # 构建提示词
    prompt = build_rag_prompt(context, question, template_name)

    # 调用大语言模型并流式返回响应
    messages = [{"role": "user", "content": prompt}]
    full_response = ""

    for token in call_deepseek_stream(messages):
        full_response += token
        yield token

    # 存储来源信息用于展示
    st.session_state["last_sources"] = docs
    st.session_state["last_full_response"] = full_response


def rag_query_temp_file(file_path: str, file_name: str, question: str, k: int = 5):
    """
    对临时上传的文件执行 RAG 查询。
    返回一个生成器，逐块产出回答内容。
    """
    # 创建临时知识库
    temp_kb = "_temp_rag_session"
    try:
        from utils.knowledge_base import delete_knowledge_base
        delete_knowledge_base(temp_kb)
    except Exception:
        pass

    try:
        num_chunks = add_documents(temp_kb, file_path, file_name)
        if num_chunks == 0:
            yield "文件内容为空或无法解析，请检查文件格式。"
            return
    except Exception as e:
        yield f"文件处理失败: {str(e)}"
        return

    yield from rag_query(temp_kb, question, k=k, template_name="rag_default")

    # 清理临时数据
    try:
        from utils.knowledge_base import delete_knowledge_base
        delete_knowledge_base(temp_kb)
    except Exception:
        pass
