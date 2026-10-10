import unittest
from unittest.mock import MagicMock, patch

from agent.core.runtime import run_agent_task


class CodingRuntimeTest(unittest.TestCase):
    def test_first_code_request_only_creates_plan(self):
        store = MagicMock()
        store.get_latest_thread_plan.return_value = None
        with patch("agent.core.runtime.get_store", return_value=store), patch(
            "agent.core.runtime._read_only_reply", return_value="实施方案，请确认",
        ), patch("agent.core.runtime._existing_sandbox_context", return_value="无文件",
        ), patch("agent.core.runtime.get_agent") as get_agent:
            result = run_agent_task(
                repo_url=None, prompt="实现一个计算器接口", thread_id="thread-1",
                model_id="test-model", event_sink=lambda *_: None,
            )
        self.assertEqual(result["final_answer"], "实施方案，请确认")
        store.add_thread_plan.assert_called_once()
        get_agent.assert_not_called()

    def test_unapproved_analysis_cannot_reach_file_tools(self):
        store = MagicMock()
        store.get_latest_thread_plan.return_value = None
        with patch("agent.core.runtime.get_store", return_value=store), patch(
            "agent.core.runtime._read_only_reply", return_value="当前没有项目文件",
        ), patch("agent.core.runtime._existing_sandbox_context", return_value="无文件"), patch(
            "agent.core.runtime.get_agent",
        ) as get_agent:
            result = run_agent_task(
                repo_url=None, prompt="这是什么项目？", thread_id="thread-1",
                model_id="test-model", event_sink=lambda *_: None,
            )
        self.assertEqual(result["final_answer"], "当前没有项目文件")
        get_agent.assert_not_called()

    def test_explicit_approval_runs_only_sandbox_graph(self):
        store = MagicMock()
        store.get_latest_thread_plan.return_value = {
            "plan_id": "plan-1", "prompt": "实现计算器接口", "plan_text": "先创建文件再测试",
        }
        with patch("agent.core.runtime.get_store", return_value=store), patch(
            "agent.core.runtime.get_agent", return_value=object(),
        ) as get_agent, patch("agent.core.runtime.run_agent_with_event_stream", return_value={
            "messages": [{"type": "ai", "content": "已在沙箱完成"}],
        }) as stream:
            result = run_agent_task(
                repo_url=None, prompt="确认实施", thread_id="thread-1",
                model_id="test-model", event_sink=lambda *_: None,
            )
        self.assertEqual(result["final_answer"], "已在沙箱完成")
        store.approve_thread_plan.assert_called_once_with("plan-1")
        self.assertEqual(get_agent.call_args.args[0]["configurable"]["task_kind"], "coding")
        self.assertIn("已确认方案", stream.call_args.kwargs["content"])

    def test_financial_and_repo_input_rejected(self):
        with self.assertRaises(ValueError):
            run_agent_task(
                repo_url="https://example.com/repo", prompt="hi", thread_id="thread-1",
                model_id="test-model", event_sink=lambda *_: None,
            )


if __name__ == "__main__":
    unittest.main()
