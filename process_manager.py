"""
Subprocess management module for the Control Panel.

Handles the execution, lifecycle, and output capturing of background
Python processes (Server, Bridge, Sniffer) without blocking the main GUI thread.
"""

import os
import subprocess
import threading
from typing import Callable, Optional


class ProcessManager:
    """
    Manages the lifecycle and asynchronous log reading of a background process.
    """

    def __init__(
        self, name: str, command: list[str], log_callback: Callable[[str, str], None]
    ) -> None:
        """
        Initialize the process manager.

        Args:
            name (str): Identifier for the process (e.g., 'SERVER').
            command (list[str]): The command list to execute.
            log_callback (Callable): Function to call with new log lines.
        """
        self.name = name
        self.command = command
        self.log_callback = log_callback
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False

    def start(self) -> bool:
        """
        Start the subprocess and initialize the log reading thread.
        """
        if self.is_running:
            return False

        try:
            kwargs = {}
            if os.name == "nt":
                # Prevents empty CMD windows from popping up on Windows
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                **kwargs,
            )
            self.is_running = True

            reader_thread = threading.Thread(target=self._read_output, daemon=True)
            reader_thread.start()

            self.log_callback(self.name, f"--- {self.name} PROCESS STARTED ---")
            return True
        except Exception as e:
            self.log_callback(self.name, f"--- ERROR STARTING {self.name}: {e} ---")
            return False

    def stop(self) -> None:
        """
        Terminate the subprocess safely and release allocated ports.
        """
        if not self.is_running or not self.process:
            return

        self.is_running = False
        try:
            self.process.terminate()
            self.process.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            self.process.kill()
        except Exception as e:
            self.log_callback(self.name, f"--- ERROR STOPPING {self.name}: {e} ---")
        finally:
            self.log_callback(self.name, f"--- {self.name} PROCESS TERMINATED ---")
            self.process = None

    def _read_output(self) -> None:
        """
        Continuously read the stdout of the subprocess and pass it to the callback.
        Runs in a separate thread to prevent blocking the UI.
        """
        if not self.process or not self.process.stdout:
            return

        for line in iter(self.process.stdout.readline, ""):
            if line:
                self.log_callback(self.name, line.strip())

        self.is_running = False
