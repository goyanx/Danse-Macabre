__version__ = "1.0.0"

import json
import traceback
import os
import requests
import threading

DEFAULT_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "8"))
OPENAI_TIMEOUT = float(os.environ.get("OPENAI_CHAT_TIMEOUT_SECONDS", "20"))

def _messages_to_prompt(messages):
    lines = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        lines.append("{}: {}".format(role, content))
    lines.append("assistant:")
    return "\n".join(lines)

class CompletionJob:
    def __init__(self, messages, api_key=None, proxy=""):
        self.messages = [m.copy() for m in messages]
        self.api_key = api_key
        self.proxy = proxy
        self.result = None
        self.error = None
        self.done = False
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def __getstate__(self):
        """Keep an in-flight network worker out of Ren'Py save data."""
        state = self.__dict__.copy()
        state.pop("_thread", None)
        state["error"] = str(state.get("error") or "")
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # A request cannot safely resume after loading a save. The story uses
        # its authored fallback when a saved job has no completed result.
        self._thread = None
        if not self.done:
            self.done = True
            self.result = self.messages + [{"role": "assistant", "content": "[AI service unavailable]"}]

    def _run(self):
        try:
            self.result = completion(self.messages, api_key=self.api_key, proxy=self.proxy)
        except Exception as e:
            self.error = e
            self.result = self.messages + [{"role": "assistant", "content": "[AI service unavailable]"}]
        finally:
            self.done = True

    def assistant_content(self, fallback=""):
        if not self.done or not self.result:
            return fallback

        last_message = self.result[-1]
        if isinstance(last_message, dict):
            return last_message.get("content", fallback)

        return fallback


def completion_async(messages, api_key=None, proxy=""):
    return CompletionJob(messages, api_key=api_key, proxy=proxy)


def _completion_openai(messages, api_key, timeout=None):
    model = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.65,
            "max_tokens": int(os.environ.get("OPENAI_CHAT_MAX_TOKENS", "160")),
        },
        timeout=timeout or OPENAI_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"].get("content", "").strip()
    if not content:
        raise RuntimeError("OpenAI returned an empty response.")
    return messages + [{"role": "assistant", "content": content}]


def _completion_ollama(messages, api_key=None, timeout=None):
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    url = base_url + "/api/chat"
    model = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": int(os.environ.get("OLLAMA_NUM_PREDICT", "256")),
        },
    }

    request_timeout = timeout or DEFAULT_TIMEOUT

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=request_timeout)
        response.raise_for_status()
    except Exception as chat_error:
        generate_payload = {
            "model": model,
            "prompt": _messages_to_prompt(messages),
            "stream": False,
            "options": payload["options"],
        }
        try:
            response = requests.post(
                base_url + "/api/generate",
                json=generate_payload,
                headers=headers,
                timeout=request_timeout
            )
            response.raise_for_status()
        except Exception as generate_error:
            raise RuntimeError(
                "Ollama chat failed: {}; generate fallback failed: {}".format(
                    chat_error, generate_error
                )
            )

    try:
        resp_json = response.json()
        # Ollama-style
        if "message" in resp_json and isinstance(resp_json["message"], dict):
            content = resp_json["message"].get("content", "")
            assistant_msg = {"role": "assistant", "content": content}
            messages.append(assistant_msg)
        # Ollama generate-style
        elif "response" in resp_json:
            assistant_msg = {"role": "assistant", "content": resp_json["response"]}
            messages.append(assistant_msg)
        # Try plain content
        elif "content" in resp_json:
            assistant_msg = {"role": "assistant", "content": resp_json["content"]}
            messages.append(assistant_msg)
        # Try OpenAI-style as fallback
        elif "choices" in resp_json and resp_json["choices"]:
            completion = resp_json["choices"][0]["message"]
            messages.append(completion)
        else:
            raise RuntimeError("Unknown Ollama response format.")
    except Exception as e:
        raise RuntimeError("Ollama response parse failed: {}".format(e))

    return messages


def completion(messages, api_key=None, proxy="", callback=None, timeout=None):
    """Complete a conversation without blocking the Ren'Py UI thread."""
    working_messages = [message.copy() for message in messages]
    provider = os.environ.get("GLASSHOUSE_LLM_PROVIDER", "auto").lower()
    openai_key = api_key or os.environ.get("OPENAI_API_KEY")
    errors = []

    if provider in ("auto", "openai") and openai_key:
        try:
            result = _completion_openai(working_messages, openai_key, timeout=timeout)
            if callback:
                callback(result)
            return result
        except Exception as exc:
            errors.append("OpenAI: {}".format(exc))

    if provider in ("auto", "ollama"):
        try:
            result = _completion_ollama(working_messages, api_key=api_key, timeout=timeout)
            if callback:
                callback(result)
            return result
        except Exception as exc:
            errors.append("Ollama: {}".format(exc))

    result = working_messages + [{"role": "assistant", "content": "[AI service unavailable]"}]
    if callback:
        callback(result)
    if errors:
        print("chatgpt.completion unavailable: " + " | ".join(errors))
    return result
