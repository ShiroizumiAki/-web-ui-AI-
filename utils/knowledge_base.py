"""
基于 ChromaDB 和 LangChain 的知识库管理。
"""
import os
import shutil
from pathlib import Path

import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.api_client import LocalEmbeddings

# ChromaDB 存储目录
CHROMA_DIR = Path(__file__).parent.parent / "data" / "chroma_db"


# ============================================================
# 文档加载器
# ============================================================

def _load_pdf(file_path: str) -> list:
    from langchain_community.document_loaders import PyPDFLoader
    loader = PyPDFLoader(file_path)
    return loader.load()


def _load_txt(file_path: str) -> list:
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()


def _load_docx(file_path: str) -> list:
    from langchain_community.document_loaders import Docx2txtLoader
    loader = Docx2txtLoader(file_path)
    return loader.load()


def _load_md(file_path: str) -> list:
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()


def _load_csv(file_path: str) -> list:
    from langchain_community.document_loaders import CSVLoader
    loader = CSVLoader(file_path, encoding="utf-8")
    return loader.load()


def _load_xlsx(file_path: str) -> list:
    from langchain_community.document_loaders import UnstructuredExcelLoader
    loader = UnstructuredExcelLoader(file_path, mode="elements")
    return loader.load()


LOADER_MAP = {
    ".pdf": _load_pdf,
    ".txt": _load_txt,
    ".docx": _load_docx,
    ".md": _load_md,
    ".csv": _load_csv,
    ".xlsx": _load_xlsx,
    ".xls": _load_xlsx,
}


# ============================================================
# ChromaDB 操作
# ============================================================

def _get_chroma_client():
    """懒加载 ChromaDB 客户端。"""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def _sanitize_name(name: str) -> str:
    """清理知识库名称以兼容 ChromaDB。
    要求：3-512 个字符，仅允许 [a-zA-Z0-9._-]，以字母数字开头和结尾。
    """
    import re
    import hashlib

    # 首先尝试提取字母数字部分
    alpha_part = re.sub(r'[^a-zA-Z0-9]', '_', name)
    alpha_part = re.sub(r'_+', '_', alpha_part)
    alpha_part = alpha_part.strip('._-')

    # 如果结果太短或仅包含下划线，则使用基于哈希的名称
    alpha_only = re.sub(r'[^a-zA-Z0-9]', '', alpha_part)
    if len(alpha_only) < 3:
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:8]
        if alpha_only:
            alpha_part = f"{alpha_only}_{hash_suffix}"
        else:
            alpha_part = f"kb_{hash_suffix}"

    # 确保以字母数字开头和结尾
    alpha_part = re.sub(r'^[^a-zA-Z0-9]+', '', alpha_part)
    alpha_part = re.sub(r'[^a-zA-Z0-9]+$', '', alpha_part)
    while len(alpha_part) < 3:
        alpha_part += '0'

    return alpha_part


def _get_collection(kb_name: str):
    """获取或创建知识库对应的 ChromaDB 集合。"""
    client = _get_chroma_client()
    embedding = LocalEmbeddings()

    safe_name = _sanitize_name(kb_name)
    try:
        collection = client.get_collection(name=safe_name)
    except Exception:
        collection = client.create_collection(name=safe_name)

    return collection, embedding


def create_knowledge_base(name: str) -> bool:
    """创建新的知识库集合。创建成功返回 True。"""
    client = _get_chroma_client()
    safe_name = _sanitize_name(name)
    try:
        client.create_collection(name=safe_name)
        return True
    except Exception:
        return False  # 已存在


def delete_knowledge_base(name: str) -> bool:
    """删除知识库集合。"""
    client = _get_chroma_client()
    safe_name = _sanitize_name(name)
    try:
        client.delete_collection(name=safe_name)
        return True
    except Exception:
        return False


def list_knowledge_bases() -> list:
    """列出所有知识库集合及其文档数量。"""
    client = _get_chroma_client()
    collections = client.list_collections()
    result = []
    for col in collections:
        result.append({
            "name": col.name,
            "count": col.count(),
        })
    return result


def add_documents(kb_name: str, file_path: str, file_name: str,
                  chunk_size: int = 1000, chunk_overlap: int = 200,
                  progress_callback=None) -> int:
    """
    加载文件，分割内容，并添加到知识库。
    返回添加的文档块数量。
    """
    ext = Path(file_path).suffix.lower()
    if ext not in LOADER_MAP:
        raise ValueError(f"不支持的文件格式: {ext}")

    # 加载文档
    loader_fn = LOADER_MAP[ext]
    docs = loader_fn(file_path)

    if progress_callback:
        progress_callback(0.3)

    # 添加来源元数据
    for doc in docs:
        doc.metadata["source"] = file_name

    # 分割文档
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    if progress_callback:
        progress_callback(0.6)

    if not chunks:
        return 0

    # 获取集合和嵌入模型
    collection, embedding = _get_collection(kb_name)

    # 添加到 ChromaDB
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    embeddings = embedding.embed_documents(texts)
    ids = [f"{file_name}_{i}" for i in range(len(texts))]

    # 检查是否存在同一来源的文档并删除
    existing = collection.get()
    existing_ids = [eid for eid, meta in zip(existing.get("ids", []),
                     existing.get("metadatas", []))
                    if meta and meta.get("source") == file_name]
    if existing_ids:
        collection.delete(ids=existing_ids)

    collection.add(ids=ids, embeddings=embeddings, documents=texts,
                   metadatas=metadatas)

    if progress_callback:
        progress_callback(1.0)

    return len(chunks)


def search_knowledge_base(kb_name: str, query: str, k: int = 5) -> list:
    """在知识库中检索相关文档。"""
    collection, embedding = _get_collection(kb_name)
    query_embedding = embedding.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    docs = []
    if results and results.get("documents") and results["documents"][0]:
        for i in range(len(results["documents"][0])):
            docs.append({
                "content": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", "未知"),
                "score": 1 - results["distances"][0][i],  # 将距离转换为相似度
            })

    return docs


def get_kb_documents(kb_name: str) -> list:
    """获取知识库中所有文档及其元数据。"""
    try:
        collection, _ = _get_collection(kb_name)
        data = collection.get(include=["metadatas"])
        sources = set()
        if data and data.get("metadatas"):
            for meta in data["metadatas"]:
                if meta and "source" in meta:
                    sources.add(meta["source"])
        return sorted(list(sources))
    except Exception:
        return []


def remove_document(kb_name: str, source_name: str):
    """删除指定来源文档的所有文档块。"""
    try:
        collection, _ = _get_collection(kb_name)
        data = collection.get(include=["metadatas"])
        ids_to_delete = []
        for eid, meta in zip(data.get("ids", []), data.get("metadatas", [])):
            if meta and meta.get("source") == source_name:
                ids_to_delete.append(eid)
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)
    except Exception:
        return 0
