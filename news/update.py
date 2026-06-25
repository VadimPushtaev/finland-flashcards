#!/usr/bin/env python3
"""Run the `news/update-prompt.txt` workflow via Codex CLI."""

from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from typing import Optional

ALARMER_URL = "https://alarmerbot.getmy.dev/?key={key}&message="
ALARMER_KEY_ENV = "ALARMER_KEY"


def send_notification(text: str) -> None:
    """Отправить сообщение через AlarmerBot."""
    key = os.environ.get(ALARMER_KEY_ENV)
    if not key:
        return

    try:
        import requests  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover
        print(f"Notification skipped: failed to import requests: {exc}", file=sys.stderr)
        return

    if not text:
        return

    alarmer_url = ALARMER_URL.format(key=key)
    max_chunk = 1500
    chunks = [text[i : i + max_chunk] for i in range(0, len(text), max_chunk)]

    for index, chunk in enumerate(chunks, start=1):
        prefix = f"[{index}/{len(chunks)}]\n" if len(chunks) > 1 else ""
        try:
            r = requests.get(
                alarmer_url + requests.utils.quote(f"{prefix}{chunk}"),
                timeout=30,
            )
            print(f"Уведомление отправлено ({r.status_code})", file=sys.stderr)
        except Exception as e:  # pragma: no cover
            print(f"Ошибка при отправке уведомления: {e}", file=sys.stderr)


def _append_log(log_path: Path, header: str, body: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        if header:
            if not header.endswith("\n"):
                header += "\n"
            log_file.write(header)
        if body:
            log_file.write(body)
            if not body.endswith("\n"):
                log_file.write("\n")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    prompt_path = Path(__file__).with_name("update-prompt.txt")
    logs_dir = Path(__file__).with_name("logs")
    stdout_log_path = logs_dir / "update_stdout.log"
    stderr_log_path = logs_dir / "update_stderr.log"

    if not prompt_path.is_file():
        print(f"Missing prompt file: {prompt_path}", file=sys.stderr)
        return 2

    command = [
        "codex",
        "exec",
        "-s",
        "danger-full-access",
        "-C",
        str(repo_root),
    ]
    started_at = dt.datetime.now(dt.timezone.utc)
    stdout_tmp_path: Optional[Path] = None
    stderr_tmp_path: Optional[Path] = None
    completed: Optional[subprocess.CompletedProcess] = None

    try:
        with tempfile.NamedTemporaryFile(
            prefix="codex_news_update_stdout_", suffix=".txt", delete=False
        ) as stdout_tmp:
            stdout_tmp_path = Path(stdout_tmp.name)
        with tempfile.NamedTemporaryFile(
            prefix="codex_news_update_stderr_", suffix=".txt", delete=False
        ) as stderr_tmp:
            stderr_tmp_path = Path(stderr_tmp.name)

        if stdout_tmp_path is None or stderr_tmp_path is None:
            raise RuntimeError("Failed to create temp files")

        prompt_text = prompt_path.read_text(encoding="utf-8")
        prompt_text += (
            "\n\n"
            "Network access is approved for this run. "
            "Fetch remote URLs as needed without requesting approval. "
            "Only add facts supported by official sources (cite the URL). "
            "If you can't verify, make no repo changes and say so.\n"
        )

        with ExitStack() as stack:
            stdout_file = stack.enter_context(stdout_tmp_path.open("wb"))
            stderr_file = stack.enter_context(stderr_tmp_path.open("wb"))
            completed = subprocess.run(
                command,
                input=prompt_text.encode("utf-8"),
                stdout=stdout_file,
                stderr=stderr_file,
            )
    except FileNotFoundError:
        print("`codex` not found on PATH. Install Codex CLI to use this script.", file=sys.stderr)
        return 127
    finally:
        finished_at = dt.datetime.now(dt.timezone.utc)
        return_code_text = str(completed.returncode) if completed is not None else "n/a"
        header = (
            f"\n=== {started_at.isoformat()} -> {finished_at.isoformat()} rc={return_code_text} ===\n"
            f"$ {' '.join(command)}\n"
        )
        if stdout_tmp_path is not None and stdout_tmp_path.exists():
            stdout_text = stdout_tmp_path.read_bytes().decode("utf-8", errors="replace")
            _append_log(stdout_log_path, header, stdout_text)
            sys.stdout.write(stdout_text)
            sys.stdout.flush()
            send_notification(stdout_text)
            stdout_tmp_path.unlink(missing_ok=True)
        if stderr_tmp_path is not None and stderr_tmp_path.exists():
            stderr_text = stderr_tmp_path.read_bytes().decode("utf-8", errors="replace")
            _append_log(stderr_log_path, header, stderr_text)
            stderr_tmp_path.unlink(missing_ok=True)

    assert completed is not None
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
