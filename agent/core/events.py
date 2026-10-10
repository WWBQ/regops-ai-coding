from __future__ import annotations

import logging

from agent.core.graph import get_store

logger = logging.getLogger("agent.run.events")


def record_event(
    thread_id: str,
    key: str,
    title: str,
    *,
    kind: str = "think",
    status: str = "in_progress",
    detail: str | None = None,
) -> None:
    """写入一个可展示在前端的运行步骤。

    这个模块独立于 runtime，避免 tools 导入 runtime 时形成循环依赖。
    """

    try:
        get_store().add_run_event(
            event_id=f"{thread_id}:{key}",
            thread_id=thread_id,
            kind=kind,
            title=title,
            status=status,
            detail=detail,
        )
    except Exception:
        # 轨迹写入失败不能中断 Agent 主任务。
        logger.exception("记录运行步骤失败：thread_id=%s key=%s title=%s", thread_id, key, title)
