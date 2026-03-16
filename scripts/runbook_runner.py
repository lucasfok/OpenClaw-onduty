#!/usr/bin/env python3
import json
import os
import socket
import ssl
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone


DEFAULT_TIMEOUT = 10


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _result(name, environment, check_type, ok, details, duration_ms):
    return {
        "name": name,
        "environment": environment,
        "type": check_type,
        "ok": ok,
        "details": details,
        "duration_ms": duration_ms,
        "timestamp": _now_iso(),
    }


def run_http_check(check):
    start = time.time()
    timeout = int(check.get("timeout_seconds", DEFAULT_TIMEOUT))
    url = check["url"]
    method = check.get("method", "GET").upper()
    expected_status = int(check.get("expected_status", 200))
    expected_substring = check.get("expected_substring")

    req = urllib.request.Request(url=url, method=method)
    context = None
    if url.startswith("https://") and not check.get("verify_tls", True):
        context = ssl._create_unverified_context()  # noqa: SLF001

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except Exception as exc:
        duration_ms = int((time.time() - start) * 1000)
        return False, f"http request failed: {exc}", duration_ms

    if status != expected_status:
        duration_ms = int((time.time() - start) * 1000)
        return False, f"expected status {expected_status}, got {status}", duration_ms

    if expected_substring and expected_substring not in body:
        duration_ms = int((time.time() - start) * 1000)
        return False, f"response missing expected_substring={expected_substring!r}", duration_ms

    duration_ms = int((time.time() - start) * 1000)
    return True, f"status={status}", duration_ms


def run_tcp_check(check):
    start = time.time()
    timeout = int(check.get("timeout_seconds", DEFAULT_TIMEOUT))
    host = check["host"]
    port = int(check["port"])

    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
    except Exception as exc:
        duration_ms = int((time.time() - start) * 1000)
        return False, f"tcp connect failed: {exc}", duration_ms

    duration_ms = int((time.time() - start) * 1000)
    return True, f"connection to {host}:{port} succeeded", duration_ms


def run_command_check(check):
    start = time.time()
    timeout = int(check.get("timeout_seconds", DEFAULT_TIMEOUT))
    command = check["command"]
    expected_exit_code = int(check.get("expected_exit_code", 0))
    expected_stdout_substring = check.get("expected_stdout_substring")

    try:
        proc = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
    except Exception as exc:
        duration_ms = int((time.time() - start) * 1000)
        return False, f"command failed to run: {exc}", duration_ms

    if proc.returncode != expected_exit_code:
        duration_ms = int((time.time() - start) * 1000)
        return (
            False,
            f"exit={proc.returncode} expected={expected_exit_code} stderr={proc.stderr.strip()}",
            duration_ms,
        )

    if expected_stdout_substring and expected_stdout_substring not in proc.stdout:
        duration_ms = int((time.time() - start) * 1000)
        return False, "stdout missing expected substring", duration_ms

    duration_ms = int((time.time() - start) * 1000)
    return True, f"exit={proc.returncode}", duration_ms


def run_check(check):
    check_type = check.get("type")
    if check_type == "http":
        return run_http_check(check)
    if check_type == "tcp":
        return run_tcp_check(check)
    if check_type == "command":
        return run_command_check(check)
    return False, f"unsupported check type={check_type}", 0


def load_runbook(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "checks" not in data or not isinstance(data["checks"], list):
        raise ValueError("runbook must contain a checks array")
    return data


def main():
    runbook_path = os.environ.get("RUNBOOK_PATH", "/etc/onduty/runbook.json")
    report_path = os.environ.get("REPORT_PATH", "/workspace/reports/latest-report.json")

    runbook = load_runbook(runbook_path)
    results = []

    for check in runbook["checks"]:
        ok, details, duration_ms = run_check(check)
        results.append(
            _result(
                check.get("name", "unnamed-check"),
                check.get("environment", "default"),
                check.get("type", "unknown"),
                ok,
                details,
                duration_ms,
            )
        )

    passed = sum(1 for item in results if item["ok"])
    failed = len(results) - passed

    report = {
        "generated_at": _now_iso(),
        "runbook": runbook.get("name", "onduty-runbook"),
        "responsible_person": os.environ.get("RESPONSIBLE_PERSON"),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
        },
        "results": results,
    }

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report["summary"], ensure_ascii=False))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
