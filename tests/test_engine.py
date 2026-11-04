"""BytePlus image generation, with the provider faked."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine_bytedance import Engine, EngineError, InputFile  # noqa: E402
from engine_bytedance.transport import ProviderError  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"pixels"
MODEL = "seedream-5-0-260128"


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []
        self.downloads = []

    def request_json(self, method, path, payload=None, *, headers=None, params=None):
        self.calls.append({"method": method, "path": path, "payload": payload})
        if not self.script:
            raise AssertionError("unexpected extra request")
        response = self.script.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def download(self, url):
        self.downloads.append(url)
        return PNG

    def request_form(self, *a, **k):
        raise AssertionError("BytePlus images are JSON, never a form")

    def request_bytes(self, *a, **k):
        return PNG


def make_engine(tmp_path, monkeypatch, client, **profile):
    monkeypatch.setattr(Engine, "_client", lambda self: client)
    base = {
        "platform": "bytedance",
        "endpoint": MODEL,
        "media_type": "image",
        "parameters": {},
        "poll_interval": 0,
        "timeout_seconds": 0,
        "retry_on_429": 0,
    }
    base.update(profile)
    return Engine(base, tmp_path, api_key="ark-test")


def an_input(tmp_path, prompt="a paper lantern"):
    path = tmp_path / "shot.md"
    path.write_text(prompt + "\n")
    return InputFile(path=path, prompt=prompt)


def test_a_good_run_saves_the_image(tmp_path, monkeypatch):
    client = FakeClient([{"data": [{"url": "https://cdn.invalid/out.png"}]}])
    results = make_engine(tmp_path, monkeypatch, client).run([an_input(tmp_path)])
    assert [r.status for r in results] == ["ok"]
    assert results[0].path.read_bytes() == PNG
    assert client.calls[0]["path"] == "images/generations"
    assert client.calls[0]["payload"]["model"] == MODEL


def test_an_empty_prompt_fails_before_spending(tmp_path, monkeypatch):
    client = FakeClient([])
    results = make_engine(tmp_path, monkeypatch, client).run([an_input(tmp_path, prompt="")])
    assert results[0].status == "error"
    assert client.calls == []


def test_a_fatal_error_stops_the_batch(tmp_path, monkeypatch):
    client = FakeClient([ProviderError(401, "unauthorized")])
    results = make_engine(tmp_path, monkeypatch, client).run([an_input(tmp_path), an_input(tmp_path)])
    assert len(results) == 1


def test_a_missing_key_is_a_preflight_error(tmp_path):
    engine = Engine({"endpoint": MODEL}, tmp_path)
    try:
        engine.run([an_input(tmp_path)])
    except EngineError as exc:
        assert "ARK_API_KEY" in str(exc)
    else:
        raise AssertionError("expected EngineError")
