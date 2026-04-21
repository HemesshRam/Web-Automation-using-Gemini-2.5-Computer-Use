"""
Process Manager — Runs main.py as a subprocess and streams ALL stdout/stderr
in real-time to connected WebSocket clients.  This ensures the frontend sees
exactly the same output as the CMD window.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Set, Optional, Dict, Any
from datetime import datetime

# Project root (parent of /api)
PROJECT_ROOT = Path(__file__).parent.parent


class ProcessManager:
    """Singleton-ish manager that runs main.py and broadcasts output."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.clients: Set[asyncio.Queue] = set()
        self._output_buffer: list[Dict[str, Any]] = []
        self._max_buffer = 5000  # Keep last 5 000 lines in memory
        self._running = False
        self._start_time: Optional[float] = None
        self._task_choice: Optional[str] = None

    # ── Public API ─────────────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    @property
    def status(self) -> Dict[str, Any]:
        return {
            "running": self.is_running,
            "pid": self.process.pid if self.process else None,
            "uptime": round(time.time() - self._start_time, 1) if self._start_time and self.is_running else 0,
            "buffer_lines": len(self._output_buffer),
            "connected_clients": len(self.clients),
            "task_choice": self._task_choice,
        }

    def subscribe(self) -> asyncio.Queue:
        """Create a new subscriber queue; returns all buffered lines first."""
        q: asyncio.Queue = asyncio.Queue()
        self.clients.add(q)
        # Replay buffer to new subscriber
        for line in self._output_buffer:
            q.put_nowait(line)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self.clients.discard(q)

    async def start_process(self, task_choice: str = "1") -> Dict[str, Any]:
        """
        Launch `python main.py` and feed `task_choice` to its stdin.
        Returns immediately; output is streamed to subscribers.
        """
        if self.is_running:
            return {"error": "Process already running", "pid": self.process.pid}

        self._task_choice = task_choice
        self._output_buffer.clear()
        self._start_time = time.time()
        self._running = True

        python = sys.executable
        cmd = [python, "-u", "main.py"]  # -u = unbuffered stdout

        self._broadcast({
            "type": "system",
            "message": f"▶ Starting: {' '.join(cmd)}  (choice={task_choice})",
            "timestamp": datetime.now().isoformat(),
        })

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # merge stderr into stdout
            stdin=subprocess.PIPE,
            cwd=str(PROJECT_ROOT),
            bufsize=0,              # unbuffered
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # Feed the menu choice + any user prompt
        asyncio.get_event_loop().run_in_executor(None, self._feed_stdin, task_choice)

        # Start background reader
        asyncio.ensure_future(self._read_output())

        return {"pid": self.process.pid, "task_choice": task_choice}

    async def stop_process(self) -> Dict[str, Any]:
        """Kill the running process."""
        if not self.is_running:
            return {"error": "No process running"}
        pid = self.process.pid
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
        self._running = False
        self._broadcast({
            "type": "system",
            "message": f"■ Process {pid} terminated",
            "timestamp": datetime.now().isoformat(),
        })
        return {"killed": True, "pid": pid}

    async def send_input(self, text: str) -> Dict[str, Any]:
        """Send text to the running process's stdin."""
        if not self.is_running:
            return {"error": "No process running"}
        try:
            self.process.stdin.write(text + "\n")
            self.process.stdin.flush()
            return {"sent": text}
        except Exception as e:
            return {"error": str(e)}

    # ── Internals ──────────────────────────────────────────────────────────

    def _feed_stdin(self, choice: str):
        """Feed the menu choice (and optional prompt) to the process stdin."""
        try:
            if self.process and self.process.stdin:
                time.sleep(0.5)  # wait for menu to render
                self.process.stdin.write(choice + "\n")
                self.process.stdin.flush()
        except Exception:
            pass

    async def _read_output(self):
        """Read stdout line-by-line and broadcast to all subscribers."""
        loop = asyncio.get_event_loop()
        try:
            while self.process and self.process.poll() is None:
                line = await loop.run_in_executor(
                    None, self.process.stdout.readline
                )
                if not line:
                    break
                stripped = line.rstrip("\n\r")
                if stripped:
                    msg = {
                        "type": "output",
                        "message": stripped,
                        "timestamp": datetime.now().isoformat(),
                    }
                    self._broadcast(msg)
        except Exception:
            pass
        finally:
            # Process ended
            exit_code = self.process.returncode if self.process else -1
            self._running = False
            self._broadcast({
                "type": "system",
                "message": f"● Process exited (code {exit_code})",
                "timestamp": datetime.now().isoformat(),
            })
            self._broadcast({
                "type": "status",
                "data": self.status
            })

    def _broadcast(self, msg: Dict[str, Any]):
        """Push a message to buffer and all subscriber queues."""
        self._output_buffer.append(msg)
        if len(self._output_buffer) > self._max_buffer:
            self._output_buffer = self._output_buffer[-self._max_buffer:]
        dead = []
        for q in self.clients:
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self.clients.discard(q)


# Singleton
process_manager = ProcessManager()
