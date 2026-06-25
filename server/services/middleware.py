"""
Agent 中间件：查询重写（查询优化）。

在 Agent 调用主模型之前（before_model 钩子）触发：用便宜的小模型 DeepSeek 把用户的
原始问题改写成"独立、完整、利于检索"的查询（消解指代、展开缩写、补全限定词），
从而提升后续知识库检索的召回质量。任何异常都会安全降级为使用原始问题。
"""

import logging

from langchain.agents.middleware import before_model
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage

from server.core.config import settings
from server.services.llm import get_query_rewrite_llm

logger = logging.getLogger(__name__)

# 改写指令：只输出改写后的查询，不作答、不解释
_REWRITE_SYSTEM = (
    "你是检索查询改写助手。请把【用户问题】改写成一个独立、完整、利于在企业知识库中检索的查询："
    "结合对话历史消解指代（如“它/这个/上面提到的”），展开缩写与省略，补全主语与关键限定词；"
    "保留原意，不要回答问题，不要解释，只输出改写后的查询本身。"
)

# 参与上下文消解的最近历史消息条数
_HISTORY_WINDOW = 6

# 指代/省略类词：出现时通常需要结合上下文补全，触发改写
_REFERENTIAL_TERMS = (
    "它", "他", "她", "它们", "他们", "她们",
    "这个", "那个", "这些", "那些", "这", "那",
    "上面", "上述", "前面", "刚才", "之前", "该", "此", "其",
)

# 短问题阈值：多轮场景下过短的提问多为省略式追问，需补全
_SHORT_QUESTION_LEN = 8


def _needs_rewrite(question: str, history: list) -> bool:
    """
    启发式判断是否需要调用小模型改写，以避免对自洽问题做多余的 LLM 调用。

    仅在"存在历史对话"且"问题含指代/省略或过短"时改写——这正是需要结合上下文
    消解指代、补全省略的场景；首轮提问或自洽的完整长问题直接跳过。
    """
    has_history = any(isinstance(m, (HumanMessage, AIMessage)) for m in history)
    if not has_history:
        return False
    q = question.strip()
    if len(q) <= _SHORT_QUESTION_LEN:
        return True
    return any(term in q for term in _REFERENTIAL_TERMS)


def _format_history(messages: list) -> str:
    """把最近的人类/助手消息整理成简短文本，供改写时消解指代。"""
    recent = [m for m in messages if isinstance(m, (HumanMessage, AIMessage))][-_HISTORY_WINDOW:]
    lines: list[str] = []
    for m in recent:
        content = m.content if isinstance(m.content, str) else str(m.content)
        content = content.strip()
        if not content:
            continue
        role = "用户" if isinstance(m, HumanMessage) else "助手"
        lines.append(f"{role}：{content}")
    return "\n".join(lines)


@before_model
def query_rewrite(state, runtime):  # noqa: ARG001 - runtime 由中间件框架注入，未使用
    """在主模型调用前，将最新的用户问题改写为利于检索的查询。"""
    if not settings.deepseek_api_key:
        return None

    messages = state.get("messages", [])
    if not messages:
        return None

    # 仅在"用户刚提出新问题"时改写：工具回传后再次进入模型时最后一条不是 HumanMessage
    last = messages[-1]
    if not isinstance(last, HumanMessage) or last.id is None:
        return None

    original = (last.content if isinstance(last.content, str) else str(last.content)).strip()
    if not original:
        return None

    # 按需改写：仅多轮且含指代/省略或过短的问题才调用小模型，普通提问直接跳过省时延
    history_messages = messages[:-1]
    if not _needs_rewrite(original, history_messages):
        return None

    try:
        history = _format_history(history_messages)
        user_prompt = (
            f"对话历史：\n{history}\n\n【用户问题】{original}" if history else f"【用户问题】{original}"
        )
        resp = get_query_rewrite_llm().invoke(
            [
                {"role": "system", "content": _REWRITE_SYSTEM},
                {"role": "user", "content": user_prompt},
            ]
        )
        rewritten = (resp.content if isinstance(resp.content, str) else str(resp.content)).strip()
        if not rewritten or rewritten == original:
            return None

        logger.info("查询重写：%s -> %s", original, rewritten)
        # 用改写后的问题替换原始问题（删除原条目并追加新条目）
        return {"messages": [RemoveMessage(id=last.id), HumanMessage(content=rewritten)]}
    except Exception as exc:  # noqa: BLE001 - 改写失败安全降级为原始问题
        logger.warning("查询重写失败，使用原问题：%s", exc)
        return None
