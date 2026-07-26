import os
import sys
import time
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGES = ROOT / "game" / "python-packages"
if str(PYTHON_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGES))

import chatgpt


class ChatAdapterTests(unittest.TestCase):
    def test_prompt_conversion_preserves_roles_and_adds_assistant_turn(self):
        prompt = chatgpt._messages_to_prompt(
            [
                {"role": "system", "content": "Stay concise."},
                {"role": "user", "content": "Hello."},
            ]
        )

        self.assertIn("system: Stay concise.", prompt)
        self.assertIn("user: Hello.", prompt)
        self.assertTrue(prompt.endswith("assistant:"))

    def test_disabled_provider_returns_deterministic_fallback_without_mutation(self):
        messages = [{"role": "user", "content": "Test"}]

        with mock.patch.dict(
            os.environ,
            {"GLASSHOUSE_LLM_PROVIDER": "disabled"},
            clear=False,
        ):
            result = chatgpt.completion(messages)

        self.assertEqual(messages, [{"role": "user", "content": "Test"}])
        self.assertEqual(result[-1]["content"], "[AI service unavailable]")

    def test_async_completion_exposes_completed_result(self):
        messages = [{"role": "user", "content": "Test"}]

        def fake_completion(input_messages, api_key=None, proxy="", callback=None, timeout=None):
            return input_messages + [{"role": "assistant", "content": "Safe fallback prose."}]

        with mock.patch.object(chatgpt, "completion", side_effect=fake_completion):
            job = chatgpt.completion_async(messages)
            deadline = time.time() + 2.0
            while not job.done and time.time() < deadline:
                time.sleep(0.01)

        self.assertTrue(job.done)
        self.assertIsNone(job.error)
        self.assertEqual(job.assistant_content("fallback"), "Safe fallback prose.")
        self.assertEqual(messages, [{"role": "user", "content": "Test"}])

    def test_async_job_state_never_serializes_thread(self):
        job = object.__new__(chatgpt.CompletionJob)
        job.messages = []
        job.api_key = None
        job.proxy = ""
        job.result = None
        job.error = None
        job.done = False
        job._thread = object()

        state = job.__getstate__()

        self.assertNotIn("_thread", state)
        self.assertEqual(state["error"], "")

    def test_ollama_request_defaults_to_fast_non_reasoning_dialogue(self):
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "message": {"role": "assistant", "content": "Lila: Stay."}
        }

        with (
            mock.patch.object(chatgpt.requests, "post", return_value=response) as post,
            mock.patch.object(chatgpt, "OLLAMA_THINK", False),
            mock.patch.object(chatgpt, "OLLAMA_KEEP_ALIVE", "10m"),
            mock.patch.dict(os.environ, {"OLLAMA_NUM_PREDICT": "96"}, clear=False),
        ):
            result = chatgpt._completion_ollama(
                [{"role": "user", "content": "Stay with me."}]
            )

        payload = post.call_args.kwargs["json"]
        self.assertFalse(payload["think"])
        self.assertEqual(payload["keep_alive"], "10m")
        self.assertEqual(payload["options"]["num_predict"], 96)
        self.assertFalse(payload["stream"])
        self.assertEqual(result[-1]["content"], "Lila: Stay.")

    def test_boolean_environment_parser_accepts_explicit_values(self):
        with mock.patch.dict(os.environ, {"TEST_LLM_BOOL": "yes"}, clear=False):
            self.assertTrue(chatgpt._env_bool("TEST_LLM_BOOL", False))

        with mock.patch.dict(os.environ, {"TEST_LLM_BOOL": "off"}, clear=False):
            self.assertFalse(chatgpt._env_bool("TEST_LLM_BOOL", True))


if __name__ == "__main__":
    unittest.main()
