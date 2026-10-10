from __future__ import annotations

from agent.core.persistence import make_postgres_checkpointer, make_postgres_langgraph_store
from agent.core.settings import AGENT_DATABASE_URL
from agent.store.postgres_store import PostgresBusinessStore

_store: PostgresBusinessStore | None = None
_checkpointer = None
_langgraph_store = None
_checkpoint_conn = None
_langgraph_store_conn = None


def get_store() -> PostgresBusinessStore:
    """获取业务 PostgreSQL Store。

    Store 保存任务列表、方案、可见消息和运行状态；
    LangGraph checkpoint 保存 Agent 图状态和工具调用上下文。
    """

    global _store
    if _store is None:
        _store = PostgresBusinessStore(AGENT_DATABASE_URL)
    return _store


def get_checkpointer():
    """获取 LangGraph PostgreSQL checkpointer。

    checkpointer 负责保存 Agent 运行过程中的 messages、工具调用状态和 thread state。
    checkpoint 存在 AI Coding PostgreSQL 中，支持服务重启后恢复。
    """

    global _checkpointer, _checkpoint_conn
    if _checkpointer is None:
        _checkpointer, _checkpoint_conn = make_postgres_checkpointer(AGENT_DATABASE_URL)
    return _checkpointer


def get_langgraph_store():
    """获取 DeepAgents StoreBackend 使用的 LangGraph PostgreSQL Store。

    业务数据位于 agent schema；checkpoint 使用 LangGraph 原生表。
    这里的 Store 保存线程隔离的沙箱快照引用。
    """

    global _langgraph_store, _langgraph_store_conn
    if _langgraph_store is None:
        _langgraph_store, _langgraph_store_conn = make_postgres_langgraph_store(AGENT_DATABASE_URL)
    return _langgraph_store


def close_persistence() -> None:
    """服务关闭时释放三条持久化连接。"""
    global _store, _checkpointer, _checkpoint_conn, _langgraph_store, _langgraph_store_conn
    for resource in (_store, _checkpoint_conn, _langgraph_store_conn):
        if resource is not None:
            resource.close()
    _store = None
    _checkpointer = _checkpoint_conn = None
    _langgraph_store = _langgraph_store_conn = None


def build_agent(thread_id: str, task_kind: str = "coding"):
    """构建一个绑定 thread_id 的 DeepAgent 兼容入口。

    真实创建逻辑已经迁移到 `agent.server.get_agent(config)`，这样项目结构更接近
    open-swe 的 LangGraph Server 入口。保留这个函数是为了兼容现有脚本和已有
    FastAPI runtime 调用点。
    """

    from agent.server import get_agent

    return get_agent(
        {
            "configurable": {
                "thread_id": thread_id,
                "task_kind": task_kind,
                "__is_for_execution__": True,
            }
        }
    )
