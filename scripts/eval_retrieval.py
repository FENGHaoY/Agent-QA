"""
检索效果评测脚本：对比"仅向量检索（baseline）"与"混合检索+RRF+Rerank（optimized）"。

在已入库 test_docs 的前提下，用一组改写过的问题（非文档原标题）做检索，
统计 Hit@1 / Hit@3 / MRR 三个指标，量化检索优化带来的提升。

运行：uv run python scripts/eval_retrieval.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# 允许以脚本方式直接运行：把项目根目录加入模块搜索路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.services import rag_service  # noqa: E402
from server.services.rag_service import get_vectorstore  # noqa: E402

# 评测集：每条为 (问题, 期望命中的文档标题)。title = 文件名去扩展名（后端入库规则）。

# 原始集：对应 test_docs/ 的 12 篇文档，主题互不重叠，检索较容易。
EASY_SET: list[tuple[str, str]] = [
    ("员工离职需要提前多少天提出申请", "员工手册"),
    ("工作日加班的加班费怎么计算", "考勤与休假管理制度"),
    ("出差期间每天的餐饮补贴是多少", "差旅报销管理办法"),
    ("密码多少天必须更换一次", "IT账号与密码安全规范"),
    ("办公设备出现故障如何报修", "办公设备领用与使用说明"),
    ("公司的数据保密分为哪几个等级", "信息安全与数据保密制度"),
    ("公司为员工提供哪些补充福利", "员工福利与五险一金说明"),
    ("绩效考核结果分为哪几个等级", "绩效考核管理办法"),
    ("新员工入职培训有多长时间", "新员工入职指引"),
    ("公司的企业愿景是什么", "公司简介与组织架构"),
    ("忘记打卡了可以补卡吗", "常见问题FAQ汇总"),
    ("VPN 连接失败了应该怎么办", "远程办公与VPN使用指南"),
]

# 易混淆集：对应 eval_docs/ 的 12 篇文档，4 个"同族"文档结构高度相似。
# 关键：问题里【不含】文档标题中的编号/版本号，而改用"品牌/功能/型号"等内容词，
# 且这些线索往往落在与答案不同的段落。这类查询纯向量易在族内混淆，
# 而 BM25 关键词召回 + Rerank 可凭精确 token 命中正确文档——优化收益在此体现。
HARD_SET: list[tuple[str, str]] = [
    ("康明斯发电机部署在哪个数据中心", "数据中心运维手册-IDC-BJ-01"),
    ("卡特彼勒发电机用于哪个机房", "数据中心运维手册-IDC-SH-02"),
    ("沃尔沃柴油发电机配置在哪个数据中心", "数据中心运维手册-IDC-GZ-03"),
    ("取消订单的接口属于哪个微服务", "微服务接口文档-订单服务ORD-SVC"),
    ("签名校验失败是哪个微服务返回的错误", "微服务接口文档-支付服务PAY-SVC"),
    ("内部调用采用 mTLS 的是哪个微服务", "微服务接口文档-库存服务INV-SVC"),
    ("哪个版本新增了多轮对话上下文记忆", "灵犀智能客服平台-v3.1发布说明"),
    ("哪个版本新增了工单自动分类能力", "灵犀智能客服平台-v3.2发布说明"),
    ("哪个版本新增了基于大模型的 RAG 智能问答", "灵犀智能客服平台-v4.0发布说明"),
    ("采购戴尔 R750 服务器的是哪张采购订单", "采购订单-PO-2024-0312"),
    ("采购华为千兆交换机的是哪张采购订单", "采购订单-PO-2024-0418"),
    ("采购 NetApp 全闪存存储的是哪张采购订单", "采购订单-PO-2024-0529"),
]

# 刁钻集：刻意构造"硬负样本"——查询里的关键词在【干扰文档】中也出现，
# 但语义/归属不同（如跨文档同名、同词不同义、同供应商不同设备、相近数值）。
# 纯向量极易被表面词面相似带偏，需 BM25 精确召回 + Rerank 结合上下文纠正。
TRICKY_SET: list[tuple[str, str]] = [
    # 跨文档同名陷阱：李雷既是 PO-0418 收货人，也是 IDC-SH-02 机房主管
    ("收货人是李雷的那张采购订单采购了什么设备", "采购订单-PO-2024-0418"),
    ("收货人为陈明的采购订单采购的是什么设备", "采购订单-PO-2024-0529"),
    # 同供应商不同设备：鼎信科技同时供货 PO-0312（服务器）与 PO-0529（存储）
    ("鼎信科技供货的那张全闪存存储采购订单是哪个", "采购订单-PO-2024-0529"),
    # 同词不同义：库存不足在 ORD-40901(无法下单) 与 INV-60001(扣减失败) 均出现
    ("库存不足导致无法下单的错误码属于哪个微服务", "微服务接口文档-订单服务ORD-SVC"),
    ("库存不足导致扣减失败的错误码属于哪个微服务", "微服务接口文档-库存服务INV-SVC"),
    # 相近数值区分：质保年限 3/1/5 年分属不同采购订单
    ("提供五年整机质保的是哪一张采购订单", "采购订单-PO-2024-0529"),
    ("故障两小时响应、7×24 原厂支持的采购订单是哪张", "采购订单-PO-2024-0529"),
    # 数值/编号埋在正文：PUE 1.30 / 网段 / 并发会话数 500
    ("设计 PUE 最低、为 1.30 的数据中心是哪个", "数据中心运维手册-IDC-SH-02"),
    ("核心网段为 10.30.0.0/16 的机房是哪个", "数据中心运维手册-IDC-GZ-03"),
    ("单实例最大并发会话数提升到 500 的是哪个版本", "灵犀智能客服平台-v3.2发布说明"),
    # 唯一专名但落在干扰段：维谛精密空调 / 海康门禁 / migrate 工具
    ("使用维谛 Liebert 精密空调的数据中心是哪个", "数据中心运维手册-IDC-SH-02"),
    ("升级时需要 migrate-4.0 迁移工具的是哪个版本", "灵犀智能客服平台-v4.0发布说明"),
]

# 评测分组：name -> 问答集
EVAL_GROUPS: list[tuple[str, list[tuple[str, str]]]] = [
    ("原始集 test_docs（主题互斥·易）", EASY_SET),
    ("易混淆集 eval_docs（同族仅编号区分·难）", HARD_SET),
    ("刁钻集 eval_docs（硬负样本/同名同词陷阱·更难）", TRICKY_SET),
]

TOP_K = 3


def _vector_only(query: str, k: int) -> list[str]:
    """baseline：仅向量相似度检索，返回命中文档标题列表。"""
    docs = get_vectorstore().similarity_search(query, k=k)
    return [(d.metadata or {}).get("title", "") for d in docs]


def _optimized(query: str, k: int) -> list[str]:
    """optimized：混合检索 + RRF + Rerank，返回命中文档标题列表。"""
    docs = rag_service.search(query, k=k)
    return [(d.metadata or {}).get("title", "") for d in docs]


def _hit_rank(expected: str, titles: list[str]) -> int:
    """返回期望标题在结果中的名次（从 1 开始）；未命中返回 0。"""
    for i, t in enumerate(titles, start=1):
        if t == expected:
            return i
    return 0


def _evaluate(eval_set: list[tuple[str, str]], retriever, *, verbose: bool = True) -> dict:
    hit1 = hit3 = 0
    mrr_sum = 0.0
    n = len(eval_set)
    for question, expected in eval_set:
        titles = retriever(question, TOP_K)
        rank = _hit_rank(expected, titles)
        if rank == 1:
            hit1 += 1
        if 1 <= rank <= 3:
            hit3 += 1
        if rank:
            mrr_sum += 1.0 / rank
        if verbose:
            flag = f"命中@{rank}" if rank else "未命中"
            print(f"  [{flag}] {question}  ->  期望《{expected}》| Top{TOP_K}: {titles}")
    return {"Hit@1": hit1 / n, "Hit@3": hit3 / n, "MRR": mrr_sum / n}


def _print_table(base: dict, opt: dict) -> None:
    print(f"  {'指标':<8}{'Baseline':>12}{'Optimized':>14}{'提升':>12}")
    for metric in ("Hit@1", "Hit@3", "MRR"):
        b, o = base[metric], opt[metric]
        print(f"  {metric:<8}{b:>12.3f}{o:>14.3f}{o - b:>+12.3f}")


def main() -> None:
    total = len(get_vectorstore().get(include=[]).get("ids") or [])
    print(f"知识库切片数：{total}；Top-K={TOP_K}")
    print("提示：易混淆集需先入库 eval_docs/ 的 12 篇文档，否则该组指标无意义。")

    for name, eval_set in EVAL_GROUPS:
        print(f"\n{'=' * 60}\n评测分组：{name}（{len(eval_set)} 题）\n{'=' * 60}")

        print("\n-- Baseline（仅向量检索）--")
        base = _evaluate(eval_set, _vector_only)

        print("\n-- Optimized（混合检索 + RRF + Rerank）--")
        opt = _evaluate(eval_set, _optimized)

        print("\n-- 指标对比 --")
        _print_table(base, opt)


if __name__ == "__main__":
    main()
