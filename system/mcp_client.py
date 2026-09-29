"""Minimal MCP stdio client for the two LOCAL YouTube MCP servers in this repo.

Stage scripts (seo_stage6 / upload_stage7 / poster) "call the YouTube MCP
tools" by speaking MCP over stdio to the SAME servers opencode uses, so:
  - auth stays in the servers (youtube-mcp-server token / .env API key)
  - tool signatures stay single-sourced (no re-implemented YouTube API calls)

Usage:
    from mcp_client import call_tool
    text = call_tool("youtube", "youtube_whoami")
    text = call_tool("youtube-seo", "get_tag_analysis", {"channel_url": "@x"})

Framing: MCP stdio = newline-delimited JSON-RPC 2.0. Servers log to stderr;
any non-JSON stdout line is skipped defensively.
"""
import atexit
import json
import os
import queue
import subprocess
import sys
import threading

PROJ = r"D:\youtube system"
PY = (r"C:\Users\bhavesh jeengar\AppData\Local\Programs\Python"
      r"\Python312\python.exe")
SERVERS = {
    "youtube": os.path.join(PROJ, "system", "youtube-mcp-server", "server.py"),
    "youtube-seo": os.path.join(PROJ, "system", "youtube-mcp-seo", "server.py"),
}


class MCPError(RuntimeError):
    """Transport/protocol failure talking to an MCP server."""


class _Conn:
    def __init__(self, server: str):
        script = SERVERS.get(server)
        if not script or not os.path.isfile(script):
            raise MCPError(f"unknown/missing MCP server: {server!r}")
        python = PY if os.path.isfile(PY) else sys.executable
        self.proc = subprocess.Popen(
            [python, "-X", "utf8", script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(script),
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        self._id = 0
        self._q: "queue.Queue[dict]" = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        # MCP handshake: initialize -> initialized notification
        self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "yt-pipeline-stage", "version": "1.0"},
        }, id_=1)
        self._recv(1, timeout=60)
        self._send("notifications/initialized", {})

    def _reader(self):
        try:
            for line in self.proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    self._q.put(json.loads(line))
                except json.JSONDecodeError:
                    pass  # stray log line on stdout — ignore
        except (ValueError, OSError):
            pass

    def _send(self, method, params, id_=None):
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        if id_ is not None:
            msg["id"] = id_
        try:
            self.proc.stdin.write(json.dumps(msg) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            raise MCPError(f"server pipe broken: {e}") from e

    def _recv(self, msg_id, timeout):
        """Wait for the response with the given JSON-RPC id (skips notifications)."""
        import time
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise MCPError(f"timed out after {timeout}s waiting for id={msg_id}")
            try:
                msg = self._q.get(timeout=min(remaining, 5))
            except queue.Empty:
                if self.proc.poll() is not None:
                    raise MCPError(f"server exited rc={self.proc.returncode}")
                continue
            if msg.get("id") == msg_id and ("result" in msg or "error" in msg):
                return msg

    def call(self, tool, arguments=None, timeout=180):
        self._id += 1
        my_id = self._id
        self._send("tools/call", {"name": tool, "arguments": arguments or {}},
                   id_=my_id)
        msg = self._recv(my_id, timeout)
        if "error" in msg:
            raise MCPError(f"{tool}: {msg['error']}")
        res = msg.get("result", {})
        parts = [c.get("text", "") for c in res.get("content", [])
                 if c.get("type") == "text"]
        text = "\n".join(parts).strip()
        if res.get("isError"):
            raise MCPError(f"{tool}: {text}")
        return text

    def close(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        except Exception:  # noqa: BLE001 — best-effort teardown
            try:
                self.proc.kill()
            except Exception:  # noqa: BLE001
                pass


_conns: dict = {}


def call_tool(server: str, tool: str, arguments=None, timeout=180) -> str:
    """Call an MCP tool on a local server; returns the tool's text result."""
    conn = _conns.get(server)
    if conn is None:
        conn = _conns[server] = _Conn(server)
        atexit.register(conn.close)
    return conn.call(tool, arguments, timeout)
