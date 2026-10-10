import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from agent.api.auth import require_regops_user
from agent.app import app


USER_ID = "00000000-0000-0000-0000-000000000001"
THREAD_ID = f"{USER_ID}_coding_11111111-1111-1111-1111-111111111111"


class StandaloneApiTest(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[require_regops_user] = lambda: USER_ID
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()

    def test_financial_routes_are_not_registered(self):
        self.assertEqual(self.client.get("/regops/agent/threads").status_code, 404)
        self.assertEqual(self.client.post("/regops/agent/threads/stream-message", json={"content": "hi"}).status_code, 404)

    def test_coding_thread_cannot_cross_owner_boundary(self):
        with patch("agent.api.coding_agent.get_task") as get_task:
            response = self.client.get("/regops/coding-agent/threads/other_coding_11111111-1111-1111-1111-111111111111")
        self.assertEqual(response.status_code, 404)
        get_task.assert_not_called()

    def test_saved_history_survives_reload_without_financial_checkpoint_parser(self):
        thread = {"thread_id": THREAD_ID, "title": "实现计算器", "latest_run_status": "completed"}
        store = MagicMock()
        store.list_thread_messages.return_value = [
            {"message_id": "user-1", "author": "user", "content": "实现计算器"},
            {"message_id": "agent-1", "author": "agent", "content": "方案如下"},
        ]
        with patch("agent.api.coding_agent.get_task", return_value=thread), patch(
            "agent.api.coding_agent.get_store", return_value=store,
        ), patch("agent.api.coding_agent.recall_snapshot", return_value=None):
            response = self.client.get(f"/regops/coding-agent/threads/{THREAD_ID}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([m["author"] for m in response.json()["messages"]], ["user", "agent"])


if __name__ == "__main__":
    unittest.main()
