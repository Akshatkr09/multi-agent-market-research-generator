"""Persistent JSON benchmarking for CrewAI workflow runs."""
from __future__ import annotations

import json
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BenchmarkRecorder:
    """Record run-level timing and task completion/routing observations.

    CrewAI's task callback fires on completion, not at task start. Therefore
    task durations here are measured as completion intervals (from kickoff or
    the preceding callback), and are labelled accordingly rather than claimed
    as exact isolated model execution times.
    """

    def __init__(self, benchmark_path: str | Path = "benchmarks.json"):
        self.path = Path(benchmark_path)
        self._lock = threading.Lock()
        self._run: dict[str, Any] | None = None
        self._started = 0.0
        self._last_completion = 0.0

    def start_run(self, query: str, csv_path: str, output_path: str) -> str:
        now = time.monotonic()
        run_id = str(uuid.uuid4())
        self._started = now
        self._last_completion = now
        self._run = {
            "run_id": run_id,
            "query": query,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "running",
            "input_csv": str(csv_path),
            "output_pdf": str(output_path),
            "total_duration_seconds": None,
            "tasks": [],
            "routing_history": [],
        }
        return run_id

    def record_task_completion(self, task_output: Any) -> None:
        if self._run is None:
            return
        now = time.monotonic()
        interval = round(max(0.0, now - self._last_completion), 3)
        self._last_completion = now
        task_obj = getattr(task_output, "task", None)
        description = (
            getattr(task_obj, "description", None)
            or getattr(task_output, "description", None)
            or "Task description unavailable"
        )
        agent = (
            getattr(task_output, "agent", None)
            or getattr(task_obj, "agent", None)
            or "Unreported"
        )
        if not isinstance(agent, str):
            agent = getattr(agent, "role", None) or str(agent)
        task_name = str(description).strip().splitlines()[0][:180]
        entry = {
            "task": task_name,
            "agent": str(agent),
            "completion_interval_seconds": interval,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }
        with self._lock:
            self._run["tasks"].append(entry)
            self._run["routing_history"].append({
                "sequence": len(self._run["routing_history"]) + 1,
                "task": task_name,
                "assigned_agent": str(agent),
                "event": "task_completed",
                "timestamp": entry["completed_at"],
            })

    def finish_run(self, status: str, error: str | None = None) -> dict[str, Any]:
        if self._run is None:
            raise RuntimeError("No benchmark run has been started.")
        self._run["total_duration_seconds"] = round(time.monotonic() - self._started, 3)
        self._run["finished_at"] = datetime.now(timezone.utc).isoformat()
        self._run["status"] = status
        if error:
            self._run["error"] = error
        self._persist()
        completed = self._run
        self._run = None
        return completed

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            existing = []
            if self.path.exists():
                try:
                    data = json.loads(self.path.read_text(encoding="utf-8"))
                    existing = data if isinstance(data, list) else data.get("runs", [])
                except (json.JSONDecodeError, OSError):
                    existing = []
            existing.append(self._run)
            payload = {"schema_version": 1, "runs": existing}
            temporary = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            temporary.replace(self.path)


def load_benchmarks(path: str | Path = "benchmarks.json") -> dict[str, Any]:
    """Load benchmark history, returning an empty schema when not yet present."""
    target = Path(path)
    if not target.exists():
        return {"schema_version": 1, "runs": []}
    return json.loads(target.read_text(encoding="utf-8"))
