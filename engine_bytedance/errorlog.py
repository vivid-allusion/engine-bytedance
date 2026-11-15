"""A verbose ``<stamp>-<stem>-<idx>_ERROR.log`` beside the would-be output of a failed item."""

from __future__ import annotations

import json
import re
import traceback
from datetime import datetime
from pathlib import Path

from . import outputs
from .datatypes import InputFile

_MASKED = "***MASKED***"
_SECRET_FIELD_RE = re.compile(
    r'("[^"]*(?:api[_-]?key|token|secret|password|authorization)[^"]*"\s*:\s*)"[^"]*"',
    re.IGNORECASE,
)


def _block(value) -> str:
    text = "null" if value is None else json.dumps(value, indent=2, ensure_ascii=False, default=str)
    return _SECRET_FIELD_RE.sub(rf'\g<1>"{_MASKED}"', text)


def write_error_log(
    *, dest_dir: Path, item: InputFile, index: int, current: int, total: int, profile: dict,
    api_key: str, expected: Path | None, stage: str, error_msg: str, payload: dict | None = None,
    error: BaseException | None = None, task_id: str = "",
) -> Path | None:
    """Write the log and return its path; never raises (the failed result still reports the failure)."""
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        path = dest_dir / outputs.output_name(item.path.stem, index, "_ERROR.log")
        trace = ("".join(traceback.format_exception(type(error), error, error.__traceback__)).rstrip()
                 if error is not None else "n/a")
        lines = [
            f"{path.name} — generation failure",
            f"when: {datetime.now().astimezone().isoformat()}",
            f"item: {current} of {total}",
            f"source: {Path(item.path).resolve()}",
            f"expected: {expected.resolve() if expected is not None else 'n/a'}",
            f"endpoint: {profile.get('endpoint', '')}",
            "profile:",
            _block(profile),
            f"prompt: {item.prompt or '(empty)'}",
            f"error stage: {stage}",
            f"byteplus task id: {task_id or 'n/a'}",
            f"error: {error_msg or 'n/a'}",
            "traceback:",
            trace,
            "request sent:",
            _block(payload),
        ]
        text = "\n".join(lines) + "\n"
        if api_key:
            text = text.replace(api_key, _MASKED)
        path.write_text(text, encoding="utf-8")
        return path
    except Exception:  # noqa: BLE001 - a log that cannot be written must not hide the failure
        return None


def attach(metadata: dict, *, output_dir: Path, item: InputFile, index: int, total: int,
           stage: str = "", error: BaseException | None = None, task_id: str = "", **fields) -> None:
    """Write the log beside the would-be output and name it in ``metadata["error_log"]``."""
    task_id = task_id or getattr(error, "task_id", "")
    if not stage:
        stage = ("task ended or timed out" if getattr(error, "task_id", "")
                 else "saving the output" if task_id else "creating the task")
    rel_dir = str(item.metadata.get("relative_dir", "") or "")
    log = write_error_log(dest_dir=output_dir / rel_dir if rel_dir else output_dir, item=item,
                          index=index, current=index + 1, total=total, stage=stage, error=error,
                          task_id=task_id, **fields)
    if log:
        metadata["error_log"] = str(log)
