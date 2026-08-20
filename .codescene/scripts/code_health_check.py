#!/usr/bin/env python3
"""MCP client: calls CodeScene analyze_change_set and enforces quality gates.

Usage:
  CS_ACCESS_TOKEN=pat_xxx python code_health_check.py --base-ref origin/main --repo .

Exits 0 if quality gates pass, 1 if any file degrades or gates fail.
Requires: npx / npm (installs @codescene/codehealth-mcp on first run).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time


def _send(proc, msg):
    line = json.dumps(msg) + "\n"
    proc.stdin.write(line)
    proc.stdin.flush()


def _recv(proc, timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.01)
            continue
        stripped = line.strip()
        if not stripped:
            continue
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            continue
    raise TimeoutError("No MCP response within timeout")


def call_analyze_change_set(base_ref, repo_path, binary="npx"):
    cmd = [binary, "-y", "@codescene/codehealth-mcp"]
    env = dict(os.environ)
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    try:
        _send(proc, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ci-codehealth", "version": "1.0"},
            },
        })
        init_resp = _recv(proc, timeout=30)
        if "error" in init_resp:
            raise RuntimeError(f"Init failed: {init_resp['error']}")

        _send(proc, {
            "jsonrpc": "2.0", "method": "notifications/initialized",
            "params": {},
        })

        _send(proc, {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {
                "name": "analyze_change_set",
                "arguments": {
                    "base_ref": base_ref,
                    "git_repository_path": os.path.abspath(repo_path),
                },
            },
        })
        result = _recv(proc, timeout=120)
        if "error" in result:
            raise RuntimeError(f"Tool call failed: {result['error']}")
        return result.get("result", {})
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def evaluate(result):
    text = result.get("content", [{}])[0].get("text", "") if isinstance(result.get("content"), list) else str(result)
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        data = result if isinstance(result, dict) else {}

    gates = data.get("quality_gates", {})
    passed = gates.get("status") == "passed" or gates.get("passed") is True
    results = data.get("results", [])
    degraded = [r for r in results if r.get("verdict") == "degraded"]

    print(f"Quality gates: {gates.get('status', 'unknown')}")
    meta = data.get("metadata", {})
    print(f"Checked files: {meta.get('checked-file-count', '?')}")
    for r in results:
        print(f"  {r.get('verdict', '?'):10s}  {r.get('name', '?')}")
        for f in r.get("findings", []):
            print(f"             {f}")

    if not passed:
        print("\n❌ Code Health quality gates FAILED.")
        return 1
    if degraded:
        print(f"\n❌ {len(degraded)} file(s) degraded.")
        return 1
    print("\n✅ Code Health quality gates passed.")
    return 0


def main():
    p = argparse.ArgumentParser(description="CodeScene CI code health gate")
    p.add_argument("--base-ref", default="origin/main", help="Base git ref to compare against")
    p.add_argument("--repo", default=".", help="Git repository path")
    p.add_argument("--binary", default="npx", help="MCP server binary (npx or cs-mcp)")
    args = p.parse_args()

    if not os.environ.get("CS_ACCESS_TOKEN"):
        print("❌ CS_ACCESS_TOKEN not set. Create a CodeScene PAT and add as GitHub secret.", file=sys.stderr)
        return 2

    try:
        result = call_analyze_change_set(args.base_ref, args.repo, args.binary)
    except Exception as e:
        print(f"❌ CodeScene analysis error: {e}", file=sys.stderr)
        return 2

    return evaluate(result)


if __name__ == "__main__":
    sys.exit(main())
