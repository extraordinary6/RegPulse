"""Tests for CLI entrypoint wiring."""

from __future__ import annotations

import runpy
from pathlib import Path

import src.cli


def test_main_py_delegates_to_src_cli_run(monkeypatch):
    """The repo-root entrypoint should be a thin wrapper around src.cli.run."""
    called = {"count": 0}

    def fake_run(argv=None):
        called["count"] += 1
        assert argv is None

    monkeypatch.setattr(src.cli, "run", fake_run)

    main_path = Path(__file__).resolve().parents[1] / "main.py"
    runpy.run_path(str(main_path), run_name="__main__")

    assert called["count"] == 1
