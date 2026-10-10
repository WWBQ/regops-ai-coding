"""AI Coding graph factory."""

from __future__ import annotations

from deepagents import create_deep_agent
from langgraph.graph.state import RunnableConfig

from agent.coding.factory import (
    DEFAULT_RECURSION_LIMIT,
    get_coding_agent,
    graph_loaded_for_execution,
)


def get_agent(config: RunnableConfig):
    config = dict(config or {})
    configurable = dict(config.get("configurable") or {})
    config["configurable"] = configurable
    config["recursion_limit"] = config.get("recursion_limit", DEFAULT_RECURSION_LIMIT)
    thread_id = configurable.get("thread_id")
    if not isinstance(thread_id, str) or not thread_id or not graph_loaded_for_execution(config):
        raise ValueError("缺少 AI Coding 会话或执行标记")
    return get_coding_agent(config)
