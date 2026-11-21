"""Tests for persistent workflow benchmark tracking."""
import json
from types import SimpleNamespace

from utils.benchmark import BenchmarkRecorder, load_benchmarks


def test_start_and_finish_persist_run_metadata(tmp_path):
    path = tmp_path / "benchmarks.json"
    recorder = BenchmarkRecorder(path)
    run_id = recorder.start_run("Tech research", "data.csv", "report.pdf")
    result = recorder.finish_run("success")
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert result["run_id"] == run_id
    assert result["status"] == "success"
    assert result["total_duration_seconds"] >= 0
    assert stored["schema_version"] == 1
    assert stored["runs"][0]["query"] == "Tech research"


def test_task_callback_records_agent_and_routing_history(tmp_path):
    recorder = BenchmarkRecorder(tmp_path / "benchmarks.json")
    recorder.start_run("topic", "data.csv", "out.pdf")
    task = SimpleNamespace(description="Research current market trends", agent=None)
    output = SimpleNamespace(task=task, agent="Lead Market Research Specialist")
    recorder.record_task_completion(output)
    result = recorder.finish_run("success")
    assert result["tasks"][0]["agent"] == "Lead Market Research Specialist"
    assert result["tasks"][0]["completion_interval_seconds"] >= 0
    assert result["routing_history"][0]["event"] == "task_completed"


def test_multiple_runs_are_appended_not_overwritten(tmp_path):
    path = tmp_path / "benchmarks.json"
    for query in ("first", "second"):
        recorder = BenchmarkRecorder(path)
        recorder.start_run(query, "data.csv", "out.pdf")
        recorder.finish_run("success")
    assert [run["query"] for run in load_benchmarks(path)["runs"]] == ["first", "second"]


def test_missing_benchmark_file_returns_empty_schema(tmp_path):
    assert load_benchmarks(tmp_path / "missing.json") == {
        "schema_version": 1, "runs": []
    }


def test_failed_run_persists_error(tmp_path):
    recorder = BenchmarkRecorder(tmp_path / "benchmarks.json")
    recorder.start_run("topic", "data.csv", "out.pdf")
    recorder.finish_run("failed", error="Provider unavailable")
    run = load_benchmarks(tmp_path / "benchmarks.json")["runs"][0]
    assert run["status"] == "failed"
    assert run["error"] == "Provider unavailable"
