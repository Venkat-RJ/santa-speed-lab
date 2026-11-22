"""Rerun Experiment #500 with a clean, local OpenClaw state directory."""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCE_ASSETS = HERE.parent / "source"
SOURCE_COMMIT = "94043a69f5fc1e1fc1def41b32bce744a2e5add0"
SCORER = "ui/src/pages/chat/chat-generation-speed.ts"


def check_source(source):
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if head != SOURCE_COMMIT:
        raise SystemExit(f"Unexpected OpenClaw commit: {head}")
    diff = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=source)
    if diff != (HERE / "retry-context.patch").read_bytes():
        raise SystemExit("The tracked source must contain exactly retry-context.patch.")
    manifest = json.loads((SOURCE_ASSETS / "official-measurement-sha256.json").read_text())
    for relative, expected in manifest.items():
        if hashlib.sha256((source / relative).read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Official measurement file differs: {relative}")


def prepare(source, run):
    run.mkdir(mode=0o700, parents=True)
    for name in ("state", "workspace", "xdg"):
        (run / name).mkdir(mode=0o700)
    for name in ("prompt.txt", "config.json"):
        shutil.copyfile(HERE / name, run / name)
    shutil.copyfile(HERE / "discover.py", run / "workspace" / "discover.py")
    command = [
        "corepack", "pnpm", "openclaw", "--profile", "speed-bounty", "agent", "exec",
        "--config", str(run / "config.json"), "--state-dir", str(run / "state"),
        "--cwd", str(run / "workspace"), "--code-mode", "direct", "--local-model-lean",
        "--timeout", "300", "--json", "--message-file", str(run / "prompt.txt"),
    ]
    settings = {
        "OPENCLAW_DISABLE_BUNDLED_PLUGINS": "1",
        "OPENCLAW_NO_AUTO_UPDATE": "1",
        "OPENCLAW_CACHE_TRACE": "1",
        "OPENCLAW_CACHE_TRACE_FILE": str(run / "context-trace.jsonl"),
        "LOCAL_REQUEST_OBSERVATION": str(run / "request-observations.jsonl"),
        "OPENCLAW_STATE_DIR": str(run / "state"),
        "OPENCLAW_CONFIG_PATH": str(run / "config.json"),
        "OPENCLAW_PROFILE": "speed-bounty",
        "NODE_OPTIONS": f'--max-old-space-size=2048 --no-warnings --import="{HERE / "observe-request.mjs"}"',
    }
    for kind in ("config", "data", "state", "cache"):
        settings[f"XDG_{kind.upper()}_HOME"] = str(run / "xdg" / kind)
    (run / "command.json").write_text(json.dumps({
        "argv": command, "cwd": str(source), "settings": settings,
    }, indent=2) + "\n")
    return command, settings


def execute(command, environment, source, run):
    with (run / "stdout.json").open("w") as stdout, (run / "stderr.txt").open("w") as stderr:
        with subprocess.Popen(
            command, cwd=source, env=environment, stdout=stdout, stderr=stderr,
            start_new_session=True,
        ) as process:
            try:
                return process.wait(timeout=150)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                return 124


def capture(source, run):
    database = run / "state/agents/main/agent/openclaw-agent.sqlite"
    if not database.exists():
        return False
    try:
        session = json.loads((run / "stdout.json").read_text()).get("sessionId", "")
    except json.JSONDecodeError:
        session = ""
    transcript = run / "transcript.jsonl"
    with transcript.open("w") as output:
        subprocess.run(
            ["node", "--no-warnings", HERE / "export-transcript.mjs", database, session or ""],
            stdout=output, check=True,
        )
    with (run / "official-speed.json").open("w") as output:
        subprocess.run(["node", "--no-warnings", HERE / "score.mjs", transcript, source / SCORER],
                       stdout=output, check=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("openclaw_source", type=Path)
    parser.add_argument("new_run_directory", type=Path)
    parser.add_argument("--prepare", action="store_true", help="write the command without running it")
    args = parser.parse_args()
    source, run = args.openclaw_source.resolve(), args.new_run_directory.resolve()
    check_source(source)
    if run.exists():
        raise SystemExit("Choose a new run directory.")
    if not args.prepare:
        if not os.environ.get("CEREBRAS_API_KEY"):
            raise SystemExit("Set CEREBRAS_API_KEY in the environment.")
        if subprocess.check_output(["node", "--version"], text=True).strip() != "v24.22.1":
            raise SystemExit("Use Node.js 24.22.1 to match the recorded run.")
        pnpm = subprocess.check_output(["corepack", "pnpm", "--version"], cwd=source, text=True).strip()
        if pnpm != "12.15.0":
            raise SystemExit(f"Use pnpm 12.15.0 to match the recorded run, got {pnpm}.")
    command, settings = prepare(source, run)
    print(f"Run files: {run}", flush=True)
    if args.prepare:
        return 0
    inherited = ("CEREBRAS_API_KEY", "PATH", "HOME", "USER", "LANG", "LC_ALL", "TMPDIR", "COREPACK_HOME")
    environment = {key: os.environ[key] for key in inherited if key in os.environ}
    environment.update(settings)
    with (HERE / ".replay.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise SystemExit("Another replay is running in this checkout.") from error
        code = execute(command, environment, source, run)
        check_source(source)
        if code:
            raise SystemExit(f"OpenClaw exited with status {code}. See {run / 'stderr.txt'}")
        if not capture(source, run):
            raise SystemExit("OpenClaw finished without an auditable transcript.")
        subprocess.run([sys.executable, HERE / "audit-native.py", run], check=True, timeout=55)
        pages = run / "workspace/retail-evidence"
        count = sum(len(json.loads(path.read_text())["rows"]) for path in pages.glob("*/evidence.json"))
        if count != 5:
            raise SystemExit(f"Verified {count}/5 products. This replay did not qualify.")
    print((run / "official-speed.json").read_text().strip())
    print("Verified five distinct products against the run's catalog responses and live product pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
