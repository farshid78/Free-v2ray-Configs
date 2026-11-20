"""chain_controller.py — موتورِ مدیریتِ زنجیره (فاز ۲).

یک اجرا (run) را به‌عنوانِ یک «نسل» (generation) از یک «زنجیره» (chain)
می‌پذیرد، lease را به‌صورت اتمی می‌گیرد، heartbeat می‌فرستد، پیش از
انقضای lease نسلِ بعدی را فرامی‌خواند و در پایان lease را آزاد می‌کند.

ورودی‌ها از متغیرهای محیطی یا آرگومان‌های CLI گرفته می‌شوند:
  CHAIN_ID, GENERATION, PREDECESSOR_RUN_ID, HANDOFF_ID, HANDOFF_NONCE,
  TRIGGER_REASON, EXPECTED_OWNER, SLICE_MINUTES
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import status  # noqa: E402


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    return v if v not in (None, "") else default


def _github_dispatch(repo: str, token: str, event_type: str, payload: dict) -> bool:
    url = f"https://api.github.com/repos/{repo}/dispatches"
    data = json.dumps({"event_type": event_type, "client_payload": payload}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return 200 <= r.status < 300
    except Exception as exc:
        print(f"[chain] dispatch failed: {exc}", file=sys.stderr)
        return False


def _workflow_dispatch(repo: str, token: str, workflow: str, ref: str, inputs: dict) -> bool:
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"
    data = json.dumps({"ref": ref, "inputs": inputs}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return 200 <= r.status < 300
    except Exception as exc:
        print(f"[chain] workflow dispatch failed: {exc}", file=sys.stderr)
        return False


def run_once(args: argparse.Namespace) -> int:
    chain_id = args.chain_id or _env("CHAIN_ID", "default")
    generation = int(args.generation if args.generation is not None else _env("GENERATION", "0"))
    predecessor = args.predecessor_run_id or _env("PREDECESSOR_RUN_ID")
    handoff_id = args.handoff_id or _env("HANDOFF_ID")
    handoff_nonce = args.handoff_nonce or _env("HANDOFF_NONCE")
    trigger_reason = args.trigger_reason or _env("TRIGGER_REASON", "manual")
    expected_owner = args.expected_owner or _env("EXPECTED_OWNER")
    slice_minutes = float(args.slice_minutes or _env("SLICE_MINUTES", "10"))
    owner = f"chain:{chain_id}:gen{generation}"

    print(f"[chain] chain={chain_id} gen={generation} owner={owner}")

    # ۱. اعتبارسنجیِ handoff (در این گام حداقلی: بررسیِ نسل)
    if expected_owner and expected_owner != owner:
        # expected_owner می‌تواند نامِ workflow باشد؛ فقط لاگ می‌کنیم
        print(f"[chain] note: expected_owner={expected_owner}")

    # ۲. گرفتنِ lease
    ok, token, why = status.acquire_chain_lease(
        owner=owner, run_id=handoff_id or str(generation),
        chain_id=chain_id, generation=generation, ttl_min=slice_minutes + 5,
    )
    if not ok:
        print(f"[chain] lease acquire failed: {why}", file=sys.stderr)
        return 2
    print(f"[chain] lease acquired fencing_token={token}")

    try:
        # ۳. heartbeat loop
        deadline = time.time() + slice_minutes * 60
        handoff_at = deadline - 60  # یک دقیقه مانده به پایان → فراخوانیِ نسلِ بعد
        triggered = False
        while time.time() < deadline:
            status.renew_chain_lease(owner, token, ttl_min=slice_minutes + 5)
            if (not triggered) and time.time() >= handoff_at:
                repo = _env("GITHUB_REPOSITORY")
                tok = _env("GITHUB_TOKEN")
                next_gen = generation + 1
                next_handoff = f"ho-{chain_id}-{next_gen}-{int(time.time())}"
                payload = {
                    "chain_id": chain_id,
                    "generation": next_gen,
                    "predecessor_run_id": os.environ.get("GITHUB_RUN_ID"),
                    "handoff_id": next_handoff,
                    "handoff_nonce": handoff_nonce,
                    "trigger_reason": "handoff",
                }
                if repo and tok:
                    ok2 = _workflow_dispatch(
                        repo, tok, "chain.yml", "main",
                        {
                            "chain_id": chain_id,
                            "generation": str(next_gen),
                            "predecessor_run_id": os.environ.get("GITHUB_RUN_ID", ""),
                            "handoff_id": next_handoff,
                            "handoff_nonce": handoff_nonce or "",
                            "trigger_reason": "handoff",
                            "expected_owner": owner,
                            "slice_minutes": str(slice_minutes),
                        },
                    )
                    print(f"[chain] next generation triggered: {ok2}")
                else:
                    print("[chain] no GITHUB_TOKEN/REPOSITORY — skip dispatch")
                triggered = True
            time.sleep(15)
        print("[chain] slice finished")
    finally:
        status.release_chain_lease(owner, token)
        print("[chain] lease released")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chain-id", default=None)
    ap.add_argument("--generation", type=int, default=None)
    ap.add_argument("--predecessor-run-id", default=None)
    ap.add_argument("--handoff-id", default=None)
    ap.add_argument("--handoff-nonce", default=None)
    ap.add_argument("--trigger-reason", default=None)
    ap.add_argument("--expected-owner", default=None)
    ap.add_argument("--slice-minutes", type=float, default=None)
    args = ap.parse_args()
    return run_once(args)


if __name__ == "__main__":
    raise SystemExit(main())
