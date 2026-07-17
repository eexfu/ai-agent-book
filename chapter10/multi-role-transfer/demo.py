"""
demo.py —— 实验 10-2 演示入口：多角色转换 / transfer_to_agent

一条命令即可运行：
    python demo.py

演示一个需要【多次跨领域切换】的复合任务：
    "查最新数据 → 用工具算指标 → 写成一段面向读者的话"
预期出现 triage → research → data_analysis → writing → triage 的自主移交链。
"""

from __future__ import annotations

import os
import sys

from openai import OpenAI

from roles import ROLES, DEFAULT_ROLE
from orchestrator import MultiRoleOrchestrator, C

# 尽量读取 .env（可选依赖，没装也能跑，只要 shell 里已 export）
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# 复合任务：故意跨「检索 + 计算 + 写作」三个领域，逼出多次自主移交。
COMPOSITE_TASK = (
    "我在准备一份给投资人看的材料。请帮我：\n"
    "1) 查一下中国 2021、2022、2023 三年的新能源汽车销量；\n"
    "2) 据此算出这三年的年均复合增长率(CAGR)；\n"
    "3) 把数据和这个增长率结论，写成一段面向投资人的、不超过 120 字的中文总结。"
)


def print_roster():
    """打印角色花名册，证明存在 ≥5 个角色、各有不同系统提示词/工具集。"""
    print(f"{C.BOLD}=== 角色花名册（共 {len(ROLES)} 个专业角色）==={C.RESET}")
    for name, role in ROLES.items():
        default_tag = "（默认入口）" if name == DEFAULT_ROLE else ""
        tools = role.tools + ["transfer_to_agent"]
        first_line = role.system_prompt.strip().splitlines()[0]
        print(
            f"{C.CYAN}• {name}{C.RESET} — {role.title}{default_tag}\n"
            f"    工具集: {tools}\n"
            f"    系统提示词(首句): {first_line}"
        )
    print()


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("错误：未找到环境变量 OPENAI_API_KEY。请先设置后重试。", file=sys.stderr)
        sys.exit(1)

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    client = OpenAI(api_key=api_key, base_url=base_url)

    print_roster()
    print(f"{C.BOLD}=== 开始执行复合任务（model={model}）==={C.RESET}")

    orch = MultiRoleOrchestrator(client=client, model=model, verbose=True)
    final = orch.run(COMPOSITE_TASK)

    print(f"\n{C.BOLD}================ 运行汇总 ================{C.RESET}")
    print(f"{C.MAGENTA}自主移交链:{C.RESET} {orch.handoff_chain_str()}")
    print(f"{C.MAGENTA}移交次数:{C.RESET} {len(orch.handoffs)}")
    for i, h in enumerate(orch.handoffs, 1):
        print(f"  {i}. {h.from_role} → {h.to_role}  |  reason: {h.reason}")
    print(f"\n{C.GREEN}最终成果:{C.RESET}\n{final}")


if __name__ == "__main__":
    main()
