import os
import pytest
import requests


def test_ollama_server_running():
    """Checks that the Ollama server is reachable and returns model tags."""
    url = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/tags"
    try:
        r = requests.get(url, timeout=5)
        assert r.status_code == 200, f"Unexpected status: {r.status_code}"
        data = r.json()
        assert isinstance(data, dict) and "models" in data, "Missing 'models' in response"
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama server is not reachable; skipping.")


def test_ollama_basic_generate():
    """Sends a minimal generation request to verify model responds (if available).
    Skips when the server is up but the model isn't pulled yet (404).
    """
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    url = host + "/api/generate"
    model = os.environ.get("OLLAMA_MODEL", "hf.co/defog/sqlcoder-7b-2:latest")
    payload = {
        "model": model,
        "prompt": "Return only: SELECT 1 as one",
        "options": {"num_ctx": 1024},
        "stream": False
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 404:
            pytest.skip(f"Model '{model}' not available on Ollama. Pull it with: ollama pull {model}")
        assert r.status_code == 200, f"Unexpected status: {r.status_code}"
        data = r.json()
        assert isinstance(data, dict), "Non-JSON response from Ollama"
        assert data.get("done") in (True, False), "Missing 'done' field in response"
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama server is not reachable; skipping.")

