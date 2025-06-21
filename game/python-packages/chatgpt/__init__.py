__version__ = "1.0.0"

import json
import traceback
import requests

def completion(messages, api_key=None, proxy="", callback=None):
    """
    Synchronous: blocks until the response is received.
    """
    url = "http://localhost:11434/api/chat"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-r1:8b",
        "messages": messages,
        "stream": False,
        "max_tokens": 256,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"Network error: {e}")

    try:
        resp_json = response.json()
        # Ollama-style
        if "message" in resp_json and isinstance(resp_json["message"], dict):
            content = resp_json["message"].get("content", "")
            assistant_msg = {"role": "assistant", "content": content}
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
            print("Unknown response format:", resp_json)
            raise Exception("Unknown response format")
    except Exception as e:
        print("Exception during response parsing:", e)
        print("Response content:", response.content)
        raise Exception(f"Error: {response.status_code}, {response.text}")

    # If a callback is provided, call it (for API compatibility, but not async)
    if callback:
        callback(messages)
    return messages