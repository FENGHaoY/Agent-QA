"""
问答 Agent 服务。

基于 LangChain 1.x 的 create_agent 构建检索增强问答 Agent：
- 工具一 retrieve_knowledge：检索企业内部知识库（Chroma）；
- 工具二 web_search：基于 Tavily 的联网搜索（按需启用）。
Agent 自行决定调用哪个工具，并综合结果作答；同时收集引用来源。
"""

import sqlite3
from functools import lru_cache

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver

from server.core.config import CHAT_MEMORY_DB, settings
from server.services.llm import get_llm
from server.services import rag_service
from server.services.middleware import query_rewrite

# Agent 的系统提示词（中文），约束其回答风格与工具使用策略
SYSTEM_PROMPT = (
    "你是一个企业内部知识库智能问答助手。"
    "请优先使用 retrieve_knowledge 工具检索企业内部知识库来回答用户问题；"
    "如果提供了 web_search 工具且知识库中没有相关信息，可调用 web_search 进行联网搜索。"
    "请基于检索到的内容用简洁、专业的中文作答，不要编造事实。"
    "如果无法找到答案，请如实告知用户。"
    "你具备多轮对话记忆，请结合此前的对话内容理解用户的追问与指代。"
)


@lru_cache(maxsize=1)
def get_checkpointer() -> SqliteSaver:
    """
    获取（懒加载）基于 SQLite 的会话记忆 checkpointer 单例。

    LangGraph 的 SqliteSaver 会将每个 thread_id 对应的对话状态（消息历史）持久化到
    本地 SQLite 文件，从而实现跨请求的短期会话记忆。使用 check_same_thread=False
    以兼容 FastAPI 在线程池中处理同步请求的场景。
    """
    CHAT_MEMORY_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(CHAT_MEMORY_DB), check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()
    return saver


def answer_question(
    question: str, use_web: bool = False, thread_id: str | None = None
) -> dict:
    """
    执行一次问答。

    参数：
        question:  用户问题。
        use_web:   是否启用 Tavily 联网搜索工具。
        thread_id: 会话线程标识。同一 thread_id 的多次提问共享对话记忆；
                   为 None 时表示无记忆的一次性问答。
    返回：
        dict，包含 answer（回答文本）与 sources（来源列表）。
    """
    # 每次请求使用独立的来源收集列表，避免并发污染
    collected_sources: list[dict] = []

    @tool
    def retrieve_knowledge(query: str) -> str:
        """检索企业内部知识库，返回与问题最相关的文档片段。"""
        docs = rag_service.search(query, k=4)
        if not docs:
            return "知识库中未检索到相关内容。"
        parts = []
        for doc in docs:
            title = doc.metadata.get("title", "未知文档")
            collected_sources.append({"title": title, "snippet": doc.page_content[:120], "url": None})
            parts.append(f"【来源：{title}】\n{doc.page_content}")
        return "\n\n".join(parts)

    # 组装工具列表
    tools = [retrieve_knowledge]

    if use_web:
        tavily = TavilySearch(max_results=3, tavily_api_key=settings.tavily_api_key)

        @tool
        def web_search(query: str) -> str:
            """使用 Tavily 进行联网搜索，返回最新的网络信息。"""
            result = tavily.invoke({"query": query})
            items = result.get("results", []) if isinstance(result, dict) else []
            if not items:
                return "联网搜索未返回结果。"
            parts = []
            for item in items:
                title = item.get("title", "网页结果")
                url = item.get("url")
                content = item.get("content", "")
                collected_sources.append({"title": title, "snippet": content[:120], "url": url})
                parts.append(f"【网页：{title}】({url})\n{content}")
            return "\n\n".join(parts)

        tools.append(web_search)

    # 构建并调用 Agent；挂载查询重写中间件；提供 thread_id 时启用 SQLite 会话记忆
    if thread_id:
        agent = create_agent(
            get_llm(),
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
            middleware=[query_rewrite],
            checkpointer=get_checkpointer(),
        )
        config = {"configurable": {"thread_id": thread_id}}
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]}, config=config
        )
    else:
        agent = create_agent(
            get_llm(), tools=tools, system_prompt=SYSTEM_PROMPT, middleware=[query_rewrite]
        )
        result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    # 取最后一条 AI 消息作为最终回答
    answer = ""
    for message in reversed(result.get("messages", [])):
        if isinstance(message, AIMessage) and message.content:
            answer = message.content if isinstance(message.content, str) else str(message.content)
            break

    # 对来源按标题去重
    unique_sources = []
    seen = set()
    for src in collected_sources:
        key = (src["title"], src.get("url"))
        if key not in seen:
            seen.add(key)
            unique_sources.append(src)

    return {"answer": answer or "抱歉，未能生成回答。", "sources": unique_sources}
