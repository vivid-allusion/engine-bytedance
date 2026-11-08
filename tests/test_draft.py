"""Draft mode and finishing a draft, with BytePlus faked."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine_bytedance import Engine, InputFile  # noqa: E402
from engine_bytedance.catalog import load_catalog  # noqa: E402
from tests.test_engine import MP4, FakeClient, make_engine  # noqa: E402

V25 = "dreamina-seedance-2-5-260628"


def done(tid, made):
    return [{"id": tid}, {"id": tid, "status": "succeeded", "created_at": made,
                          "content": {"video_url": "https://cdn.invalid/o.mp4"}}]


def run(tmp_path, monkeypatch, client, endpoint, item, **params):
    engine = make_engine(tmp_path, monkeypatch, client, endpoint=endpoint, media_type="video", parameters=params)
    return engine.run([item])[0]


def shot(tmp_path, prompt="a fox", **metadata):
    path = tmp_path / "S01.md"
    path.write_text(prompt + "\n")
    return InputFile(path=path, prompt=prompt, metadata=metadata)


def test_draft_mode_only_on_two_models():
    on = {s.model for s in load_catalog().specs() if s.draft_mode}
    assert on == {V25, "seedance-1-5-pro"}


def test_draft_sends_480p_and_returns_ticket(tmp_path, monkeypatch):
    client = FakeClient(done("cgt-1", 1794052583))
    monkeypatch.setattr(FakeClient, "download", lambda self, url: MP4)
    out = run(tmp_path, monkeypatch, client, V25, shot(tmp_path), draft=True, resolution="1080p")
    body = client.calls[0]["payload"]
    assert body["draft"] is True and body["resolution"] == "480p"
    assert out.metadata["draft_task"] == {"id": "cgt-1", "created_at": 1794052583,
                                          "expires_at": 1794052583 + 14 * 86400}


def test_old_draft_expires_in_seven_days(tmp_path, monkeypatch):
    client = FakeClient(done("cgt-2", 1793000000))
    monkeypatch.setattr(FakeClient, "download", lambda self, url: MP4)
    out = run(tmp_path, monkeypatch, client, "seedance-1-5-pro", shot(tmp_path), draft=True)
    assert out.metadata["draft_task"]["expires_at"] == 1793000000 + 7 * 86400


def test_draft_refused_without_draft_mode(tmp_path, monkeypatch):
    client = FakeClient([])
    out = run(tmp_path, monkeypatch, client, "dreamina-seedance-2-0-260128", shot(tmp_path), draft=True)
    assert out.status == "error" and client.calls == []


def test_finish_sends_only_the_ticket(tmp_path, monkeypatch):
    client = FakeClient(done("cgt-3", 1794060000))
    monkeypatch.setattr(FakeClient, "download", lambda self, url: MP4)
    item = shot(tmp_path, prompt="", draft_task_id="cgt-1")
    out = run(tmp_path, monkeypatch, client, V25, item, duration=5, seed=42, generate_audio=True, watermark=True)
    assert client.calls[0]["payload"] == {
        "model": V25, "content": [{"type": "draft_task", "draft_task": {"id": "cgt-1"}}],
        "resolution": "1080p", "watermark": True}
    assert out.metadata["finished_from"] == "cgt-1"
