from __future__ import annotations

import os
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
import psycopg
from psycopg.rows import dict_row


def make_postgres_checkpointer(dsn: str) -> tuple[PostgresSaver, psycopg.Connection]:
    """LangGraph 原生 PostgreSQL checkpoint，持有连接直到应用关闭。"""
    os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
    conn = psycopg.connect(dsn, autocommit=True, row_factory=dict_row, prepare_threshold=0)
    try:
        saver = PostgresSaver(conn)
        saver.setup()
        return saver, conn
    except Exception:
        conn.close()
        raise


def make_postgres_langgraph_store(dsn: str) -> tuple[PostgresStore, psycopg.Connection]:
    """DeepAgents `/memories/` 使用的 LangGraph 原生 PostgreSQL Store。"""
    conn = psycopg.connect(dsn, autocommit=True, row_factory=dict_row)
    try:
        store = PostgresStore(conn)
        store.setup()
        return store, conn
    except Exception:
        conn.close()
        raise


