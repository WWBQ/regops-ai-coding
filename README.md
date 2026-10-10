# AI Coding Harness

从 RegOps Copilot 的 AI Coding 模块独立出的沙箱化编码 Agent。原项目中的 AI Coding 代码和页面保留；本仓库拥有独立的 FastAPI 服务入口、DeepAgents 图、Skills、PostgreSQL 会话状态和 OpenSandbox 执行后端，不加载金融风险 Agent 或 MCP 工具。

## 工作方式

1. 用户提出开发任务，服务先生成只读实施方案；用户明确回复“确认实施”后，才给 DeepAgent 文件与命令工具。
2. 文件读写、测试命令只在会话专属 OpenSandbox 的 `/projects` 中执行。沙箱不可用时失败关闭，不回退宿主机 Shell。
3. PostgreSQL 保存业务会话、方案、运行记录和 LangGraph checkpoint。运行结束后，将沙箱 ZIP 快照写到可持久化的存储目录；也可切换为原 RegOps 的对象存储 API。长期 Store 只保存快照 URI 和 SHA-256，不保存临时下载链接。
4. 沙箱过期后，服务在新沙箱中校验并恢复已保存快照；用户也可以上传代码或 ZIP、导出成果。无快照时不会声称旧代码仍存在。

```text
client / existing RegOps BFF
  → FastAPI /regops/coding-agent
    → plan gate → DeepAgents + analysis sub-agent + Skills
      → OpenSandbox /projects (no host project mount)
    → PostgreSQL (sessions, plans, checkpoint, snapshot pointer)
    → local object directory or RegOps object-store API (ZIP bytes)
```

原 RegOps Vue 页面仍在原仓库；本仓库目前是独立后端，不包含第二份前端。API 路径保留 `/regops/coding-agent`，便于原 Java BFF 切换上游地址。服务令牌和用户 UUID 由可信 BFF 通过 `X-Regops-Service-Token`、`X-Regops-User` 传入；不要让浏览器持有服务令牌。

## 运行

需要 Python 3.14、PostgreSQL 和可访问的 OpenSandbox 服务。复制 `.env.example` 为 `.env`，填写数据库、模型 API Key、沙箱地址与 API Key、服务令牌；`.env` 已被 Git 忽略。

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn agent.app:app --host 127.0.0.1 --port 2025
```

`GET /health` 检查服务启动；`GET /regops/coding-agent/options` 需要 BFF 服务令牌与用户身份。`AGENT_DATABASE_URL` 指向独立 PostgreSQL 数据库；账号需要在初始化时创建 `agent` schema 及 LangGraph checkpoint/store 表的权限。

本地 kind + Kubernetes 的 OpenSandbox 部署见 [`deploy/opensandbox/README.md`](deploy/opensandbox/README.md)。在宿主机运行 Agent 时可使用 `127.0.0.1:8090` 端口转发；若 Agent 在容器中，不能把容器内 `localhost` 当作宿主机沙箱地址。部署前要运行 smoke 测试，实际验证命令、文件 API 和禁网策略。

快照后端默认 `local`，存储在 `AI_CODING_OBJECT_DIR`（默认为 `data/objects/`）；这是便于独立开发的本机持久化目录，不是生产级对象存储。生产多实例部署应配置持久对象存储及会话级分布式锁。若与原 RegOps 集成，可设 `AI_CODING_SNAPSHOT_BACKEND=regops`，并提供 `REGOPS_API_BASE_URL` 和 `REGOPS_SERVICE_TOKEN`，继续使用原对象存储私有接口。

## 接口

- `GET /regops/coding-agent/options`：可用模型与执行模式。
- `GET /regops/coding-agent/threads`、`GET /regops/coding-agent/threads/{id}`：当前用户的会话列表与历史。
- `POST /regops/coding-agent/threads/stream-message`、`POST /regops/coding-agent/threads/{id}/stream-message`：新会话或续聊，返回 SSE。
- `POST /regops/coding-agent/threads/sandbox`、`POST /regops/coding-agent/threads/{id}/sandbox`：创建、重连或恢复沙箱。
- `POST /regops/coding-agent/threads/{id}/files?filename=...`：上传代码或 ZIP，限制 20 MiB、2000 文件，拒绝越界路径及凭据文件。
- `GET /regops/coding-agent/threads/{id}/export`：导出 ZIP。
- `DELETE /regops/coding-agent/threads/{id}`：清理会话、沙箱及快照。

所有会话 ID 按用户 UUID 隔离，跨用户访问返回 404。未获确认的请求只通过不带工具的模型调用处理；已确认的开发任务才进入沙箱 DeepAgent。

## 验证

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python deploy/opensandbox/smoke.py
```

单元测试不调用真实模型或沙箱；smoke 需要已部署的 OpenSandbox 服务。当前本地 kind 仅用于开发验证，不能等同生产级多租户隔离。
