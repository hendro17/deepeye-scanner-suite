import asyncio, queue, json
import pytest
from unittest.mock import MagicMock, patch
from api.services import engine_runner

@pytest.mark.asyncio
async def test_stream_scan_not_found_exhaust():
    gen = engine_runner.stream_scan(99998)
    chunks = [c async for c in gen]
    assert any("Scan not found" in c for c in chunks)
    # ensure generator properly returned (no extra)
    assert len(chunks) == 1

@pytest.mark.asyncio
async def test_stream_scan_done_break_covered(monkeypatch):
    q = queue.Queue()
    q.put(("log", "line1", "ts1"))
    q.put(("done", "/tmp/r.json", 0))
    engine_runner.active_scans[100] = {"queue": q, "done": False, "process": MagicMock()}
    async def fake_to_thread(func, *args, **kwargs):
        return q.get_nowait()
    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    gen = engine_runner.stream_scan(100)
    outputs = [c async for c in gen]
    assert any("log" in o for o in outputs)
    assert any("done" in o for o in outputs)
    # ensure break executed - generator should be exhausted
    engine_runner.active_scans.pop(100, None)
