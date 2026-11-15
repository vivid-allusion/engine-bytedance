"""Every failed item gets its own verbose _ERROR.log, named in metadata["error_log"]."""

from pathlib import Path

from tests.test_engine import FakeClient, MODEL, an_input, make_engine
from engine_bytedance.transport import ProviderError

SEEDANCE = "dreamina-seedance-2-5-260628"


def _video(tmp_path, monkeypatch, script, **profile):
    client = FakeClient(script)
    profile.setdefault("parameters", {"api_key": "ark-test"})
    return make_engine(tmp_path, monkeypatch, client, endpoint=SEEDANCE, media_type="video", **profile)


def _log(result, tmp_path):
    path = Path(result.metadata["error_log"])
    assert path.parent == tmp_path and path.name.endswith("-0_ERROR.log")
    return path.read_text()


def test_a_failed_task_logs_the_reason_and_task_id(tmp_path, monkeypatch):
    engine = _video(tmp_path, monkeypatch, [
        {"id": "cgt-9"},
        {"id": "cgt-9", "status": "failed", "error": {"message": "text may be sensitive"}},
    ])
    result = engine.run([an_input(tmp_path)])[0]
    text = _log(result, tmp_path)
    assert "text may be sensitive" in text and "cgt-9" in text and "shot.md" in text
    assert "item: 1 of 1" in text and SEEDANCE in text
    assert "ark-test" not in text and "***MASKED***" in text


def test_a_refused_create_and_an_empty_prompt_log(tmp_path, monkeypatch):
    engine = _video(tmp_path, monkeypatch, [ProviderError(400, "bad request")])
    assert "bad request" in _log(engine.run([an_input(tmp_path)])[0], tmp_path)
    engine = make_engine(tmp_path, monkeypatch, FakeClient([]))
    assert "Empty prompt" in _log(engine.run([an_input(tmp_path, prompt="")])[0], tmp_path)


def test_no_output_and_timeout_log(tmp_path, monkeypatch):
    engine = _video(tmp_path, monkeypatch, [{"id": "t"}, {"id": "t", "status": "succeeded"}])
    assert "No output" in _log(engine.run([an_input(tmp_path)])[0], tmp_path)
    engine = _video(tmp_path, monkeypatch, [{"id": "t"}, {"id": "t", "status": "running"}],
                    timeout_seconds=0.001, poll_interval=0.01)
    assert "did not finish" in _log(engine.run([an_input(tmp_path)])[0], tmp_path)


def test_a_good_item_has_no_log_and_a_failed_one_in_a_batch_has_its_own(tmp_path, monkeypatch):
    client = FakeClient([{"data": [{"url": "https://cdn.invalid/a.png"}]}, ProviderError(400, "nope")])
    results = make_engine(tmp_path, monkeypatch, client).run([an_input(tmp_path), an_input(tmp_path)])
    assert "error_log" not in results[0].metadata
    assert "nope" in Path(results[1].metadata["error_log"]).read_text()


def test_an_unwritable_log_never_raises(tmp_path, monkeypatch):
    engine = make_engine(tmp_path, monkeypatch, FakeClient([ProviderError(400, "nope")]))
    item = an_input(tmp_path, prompt="x")
    monkeypatch.setattr(Path, "write_text", lambda *a, **k: (_ for _ in ()).throw(OSError("full")))
    result = engine.run([item])[0]
    assert result.status == "error" and "error_log" not in result.metadata


def test_a_failed_download_leaves_only_the_error_log(tmp_path, monkeypatch):
    client = FakeClient([{"data": [{"url": "https://cdn.invalid/a.png"}]}])
    monkeypatch.setattr(FakeClient, "download",
                        lambda self, url: (_ for _ in ()).throw(ProviderError(500, "download failed")))
    result = make_engine(tmp_path, monkeypatch, client).run([an_input(tmp_path)])[0]
    assert result.status == "error" and "download failed" in _log(result, tmp_path)
    assert [p.name for p in tmp_path.iterdir() if p.suffix == ".png"] == []
