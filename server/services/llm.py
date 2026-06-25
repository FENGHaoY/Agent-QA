"""
大模型与嵌入模型工厂。

通过 DashScope 的 OpenAI 兼容端点调用通义千问（Qwen）系列模型：
- 对话模型使用 ChatOpenAI；
- 嵌入模型使用 OpenAIEmbeddings（关闭本地分词以兼容 DashScope）。
"""

from functools import lru_cache

from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from server.core.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """获取对话大模型实例（带缓存，全局复用）。"""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        temperature=0.3,
    )


@lru_cache(maxsize=1)
def get_query_rewrite_llm() -> ChatDeepSeek:
    """
    获取用于查询重写的小模型实例（DeepSeek，便宜且快）。

    仅用于把用户问题改写成利于检索的查询，temperature=0 保证输出稳定。
    """
    return ChatDeepSeek(
        model=settings.query_rewrite_model,
        api_key=settings.deepseek_api_key,
        temperature=0,
    )


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    """获取嵌入模型实例（带缓存，全局复用）。"""
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        # 关闭基于 tiktoken 的本地分词，直接发送原始文本，兼容 DashScope 兼容端点
        check_embedding_ctx_length=False,
    )
