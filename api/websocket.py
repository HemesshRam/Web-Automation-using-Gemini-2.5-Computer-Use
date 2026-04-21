"""
WebSocket — Real-time Log Streaming
Two endpoints:
  /ws/logs          — tails the latest log file (original behaviour)
  /ws/live-console  — streams real-time subprocess stdout (new)
"""

import asyncio
from pathlib import Path
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from api.services import LogService
from api.process_manager import process_manager

log_service = LogService()

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


async def websocket_log_stream(websocket: WebSocket):
    """Stream log file changes in real-time via WebSocket (original)"""
    await websocket.accept()
    active_connections.add(websocket)

    try:
        log_file = log_service.get_latest_log_file()
        if not log_file or not log_file.exists():
            await websocket.send_json({"type": "info", "message": "No log file found"})
            # Wait for log file to appear
            while not log_file or not log_file.exists():
                await asyncio.sleep(2)
                log_file = log_service.get_latest_log_file()

        # Send last 50 lines initially
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            for line in lines[-50:]:
                stripped = line.strip()
                if stripped:
                    await websocket.send_json({
                        "type": "log",
                        "message": stripped
                    })

        # Tail the file
        last_size = log_file.stat().st_size
        while True:
            await asyncio.sleep(0.5)  # faster polling

            # Check if a newer log file appeared
            latest = log_service.get_latest_log_file()
            if latest and latest != log_file:
                log_file = latest
                last_size = 0

            if not log_file.exists():
                continue

            current_size = log_file.stat().st_size
            if current_size > last_size:
                with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(last_size)
                    new_lines = f.readlines()
                    for line in new_lines:
                        stripped = line.strip()
                        if stripped:
                            await websocket.send_json({
                                "type": "log",
                                "message": stripped
                            })
                last_size = current_size
            elif current_size < last_size:
                # File was truncated/rotated
                last_size = 0

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        active_connections.discard(websocket)


async def websocket_live_console(websocket: WebSocket):
    """
    Stream live subprocess output (stdout+stderr) to the browser.
    This gives the frontend the exact same output as the CMD window.
    Supports bidirectional: client can send input to the process stdin.
    """
    await websocket.accept()

    # Subscribe to process output
    queue = process_manager.subscribe()

    # Send current status
    await websocket.send_json({
        "type": "status",
        "data": process_manager.status,
    })

    reader_task = None
    writer_task = None

    async def _reader():
        """Read from queue and send to browser."""
        try:
            while True:
                msg = await queue.get()
                await websocket.send_json(msg)
        except Exception:
            pass

    async def _writer():
        """Read from browser and send to process stdin."""
        try:
            while True:
                data = await websocket.receive_json()
                action = data.get("action", "")

                if action == "start":
                    choice = data.get("choice", "1")
                    await process_manager.start_process(choice)
                    await websocket.send_json({"type": "status", "data": process_manager.status})

                elif action == "stop":
                    await process_manager.stop_process()
                    await websocket.send_json({"type": "status", "data": process_manager.status})

                elif action == "input":
                    text = data.get("text", "")
                    await process_manager.send_input(text)
                    await websocket.send_json({"type": "status", "data": process_manager.status})

                elif action == "status":
                    await websocket.send_json({"type": "status", "data": process_manager.status})

        except WebSocketDisconnect:
            pass
        except Exception:
            pass

    try:
        reader_task = asyncio.create_task(_reader())
        writer_task = asyncio.create_task(_writer())
        await asyncio.gather(reader_task, writer_task)
    except Exception:
        pass
    finally:
        if reader_task:
            reader_task.cancel()
        if writer_task:
            writer_task.cancel()
        process_manager.unsubscribe(queue)
