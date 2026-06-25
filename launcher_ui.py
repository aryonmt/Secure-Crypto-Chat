"""
Master Launcher Graphical User Interface.

Provides a unified Control Panel to manage multiple microservices concurrently,
featuring a tabbed live logging console to isolate outputs for debugging.
"""

import sys
import threading
import time
import webbrowser
from typing import Dict, List

import customtkinter as ctk

from process_manager import ProcessManager


class Palette:
    """
    Design tokens for the control panel.

    Mirrors the color system used in the web frontend (true-black surfaces,
    amber for "weak/at-risk", teal for "secure/healthy") so the desktop tool
    and the browser client read as the same product.
    """

    INK = "#09090b"
    SURFACE_1 = "#111114"
    SURFACE_2 = "#1a1a1e"
    SURFACE_3 = "#212226"
    LINE = "#2a2a30"

    TEXT_1 = "#f5f5f7"
    TEXT_2 = "#9d9da7"
    TEXT_3 = "#6b6b74"

    SECURE = "#2dd4bf"  # start / running / healthy
    DANGER = "#fb5471"  # stop / destructive
    WEAK = "#f0a942"  # warnings, sniffer accent
    INFO = "#5ab4f0"  # informational accent

    # Per-service accent, reused for the status dot on each card AND the
    # colorized "[SERVICE]" prefix in the log console.
    SERVICE_ACCENTS: Dict[str, str] = {
        "SERVER": SECURE,
        "BRIDGE": "#9b8cf0",
        "SNIFFER": WEAK,
        "WEB_SERVER": INFO,
    }


SERVICES: List[str] = ["SERVER", "BRIDGE", "SNIFFER", "WEB_SERVER"]
LOG_TABS: List[str] = ["ALL", "SYSTEM", *SERVICES]
LOG_ACCENTS: Dict[str, str] = {"SYSTEM": Palette.TEXT_2, **Palette.SERVICE_ACCENTS}


class SecureLauncherUI(ctk.CTk):
    """
    Main Application Window for the Secure Network Control Panel.
    """

    def __init__(self) -> None:
        """Initialize the UI theme, layout, and process managers."""
        super().__init__()

        self.title("Secure Chat — Master Control Panel")
        self.geometry("1180x740")
        self.minsize(960, 600)

        ctk.set_appearance_mode("dark")
        self.configure(fg_color=Palette.INK)

        self.log_boxes: Dict[str, ctk.CTkTextbox] = {}
        self.status_labels: Dict[str, ctk.CTkLabel] = {}
        self.service_running: Dict[str, bool] = {name: False for name in SERVICES}

        self._configure_grid()
        self._initialize_process_managers()
        self._build_ui()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _configure_grid(self) -> None:
        """Configure the main grid layout weights."""
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _initialize_process_managers(self) -> None:
        """Initialize the ProcessManager instances for all microservices."""
        python_exe = sys.executable
        script_by_service = {
            "SERVER": "server.py",
            "BRIDGE": "bridge.py",
            "SNIFFER": "sniffer.py",
            "WEB_SERVER": "web_server.py",
        }

        self.managers: Dict[str, ProcessManager] = {
            name: ProcessManager(name, [python_exe, script], self.append_log)
            for name, script in script_by_service.items()
        }

    def _build_ui(self) -> None:
        """Construct the UI panels and components."""
        self._build_header()
        self._build_control_panel()
        self._build_log_console()

    def _build_header(self) -> None:
        """Build the top title bar."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(22, 4), sticky="ew")

        ctk.CTkLabel(
            header,
            text="Secure Chat",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=Palette.TEXT_1,
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Master Control Panel — manage every microservice from one place",
            font=ctk.CTkFont(size=12),
            text_color=Palette.TEXT_3,
        ).pack(anchor="w")

    def _build_control_panel(self) -> None:
        """Build the master action bar and the per-service card grid."""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, padx=24, pady=(10, 6), sticky="ew")
        container.grid_columnconfigure(0, weight=1)

        self._build_master_bar(container)
        self._build_service_grid(container)

    def _build_master_bar(self, parent: ctk.CTkFrame) -> None:
        """Build the prominent Start All / Stop All bar."""
        bar = ctk.CTkFrame(
            parent,
            fg_color=Palette.SURFACE_1,
            corner_radius=12,
            border_width=1,
            border_color=Palette.LINE,
        )
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bar,
            text="Master controls",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Palette.TEXT_1,
        ).grid(row=0, column=0, sticky="w", padx=16, pady=12)

        actions = ctk.CTkFrame(bar, fg_color="transparent")
        actions.grid(row=0, column=1, padx=16, pady=10, sticky="e")

        ctk.CTkButton(
            actions,
            text="Start all",
            width=120,
            corner_radius=8,
            fg_color=Palette.SECURE,
            hover_color="#25b8a5",
            text_color=Palette.INK,
            font=ctk.CTkFont(weight="bold"),
            command=self._start_all_sequence,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            actions,
            text="Stop all",
            width=120,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=Palette.LINE,
            hover_color=Palette.SURFACE_3,
            text_color=Palette.DANGER,
            font=ctk.CTkFont(weight="bold"),
            command=self._stop_all,
        ).pack(side="left")

    def _build_service_grid(self, parent: ctk.CTkFrame) -> None:
        """Build the row of individual service control cards."""
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="ew")
        grid.grid_columnconfigure(tuple(range(len(SERVICES))), weight=1)

        for column, service_name in enumerate(SERVICES):
            self._build_service_card(grid, service_name, column)

    def _build_service_card(
        self, parent: ctk.CTkFrame, service_name: str, column: int
    ) -> None:
        """Build a control card for an individual service."""
        accent = Palette.SERVICE_ACCENTS[service_name]

        card = ctk.CTkFrame(
            parent,
            fg_color=Palette.SURFACE_1,
            corner_radius=12,
            border_width=1,
            border_color=Palette.LINE,
        )
        card.grid(row=0, column=column, padx=6, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=service_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Palette.TEXT_1,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 2))

        status_label = ctk.CTkLabel(
            card,
            text="● Idle",
            font=ctk.CTkFont(size=11),
            text_color=Palette.TEXT_3,
            anchor="w",
        )
        status_label.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))
        self.status_labels[service_name] = status_label

        button_row = ctk.CTkFrame(card, fg_color="transparent")
        button_row.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
        button_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_row,
            text="Start",
            corner_radius=8,
            height=30,
            fg_color=Palette.SURFACE_3,
            hover_color=accent,
            text_color=Palette.TEXT_1,
            font=ctk.CTkFont(size=12),
            command=lambda: self._start_service(service_name),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            button_row,
            text="Stop",
            corner_radius=8,
            height=30,
            fg_color="transparent",
            border_width=1,
            border_color=Palette.LINE,
            hover_color=Palette.SURFACE_3,
            text_color=Palette.TEXT_2,
            font=ctk.CTkFont(size=12),
            command=lambda: self._stop_service(service_name),
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def _build_log_console(self) -> None:
        """Build the tabbed live terminal output textboxes."""
        log_frame = ctk.CTkFrame(
            self,
            fg_color=Palette.SURFACE_1,
            corner_radius=12,
            border_width=1,
            border_color=Palette.LINE,
        )
        log_frame.grid(row=2, column=0, padx=24, pady=(6, 22), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            log_frame,
            text="\u203a_ ISOLATED TERMINAL CONSOLES",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=Palette.TEXT_2,
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        self.tabview = ctk.CTkTabview(
            log_frame,
            fg_color=Palette.SURFACE_1,
            segmented_button_fg_color=Palette.SURFACE_3,
            segmented_button_selected_color=Palette.SURFACE_2,
            segmented_button_selected_hover_color=Palette.SURFACE_2,
            segmented_button_unselected_color=Palette.SURFACE_3,
            segmented_button_unselected_hover_color=Palette.SURFACE_2,
            text_color=Palette.TEXT_1,
            corner_radius=10,
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        for tab_name in LOG_TABS:
            self.tabview.add(tab_name)
            self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)
            self.tabview.tab(tab_name).grid_rowconfigure(0, weight=1)

            textbox = ctk.CTkTextbox(
                self.tabview.tab(tab_name),
                fg_color=Palette.INK,
                text_color=Palette.TEXT_2,
                corner_radius=8,
                border_width=1,
                border_color=Palette.LINE,
                font=ctk.CTkFont(family="Consolas", size=12),
            )
            textbox.grid(row=0, column=0, sticky="nsew")

            for name, color in LOG_ACCENTS.items():
                textbox.tag_config(f"tag_{name.lower()}", foreground=color)

            self.log_boxes[tab_name] = textbox

        self.append_log(
            "SYSTEM", "Control panel initialized. Microservice tabs created."
        )

    def append_log(self, process_name: str, message: str) -> None:
        """
        Route and append a new log line to the appropriate tab(s), with the
        "[SERVICE]" prefix colorized using that service's accent.
        """
        tag = f"tag_{process_name.lower()}"
        prefix = f"[{process_name}] "
        suffix = f"{message}\n"

        if "ALL" in self.log_boxes:
            self._write_line(self.log_boxes["ALL"], prefix, suffix, tag)

        if process_name in self.log_boxes:
            self._write_line(self.log_boxes[process_name], prefix, suffix, tag)
        else:
            if "SYSTEM" in self.log_boxes:
                self._write_line(self.log_boxes["SYSTEM"], prefix, suffix, tag)

    @staticmethod
    def _write_line(box: ctk.CTkTextbox, prefix: str, suffix: str, tag: str) -> None:
        """Insert one colorized log line into a textbox and scroll to it."""
        box.insert(ctk.END, prefix, tag)
        box.insert(ctk.END, suffix)
        box.see(ctk.END)

    def _start_service(self, service_name: str) -> None:
        """Start a single service and reflect the new state on its card."""
        self.managers[service_name].start()
        self._set_service_running(service_name, True)

    def _stop_service(self, service_name: str) -> None:
        """Stop a single service and reflect the new state on its card."""
        self.managers[service_name].stop()
        self._set_service_running(service_name, False)

    def _set_service_running(self, service_name: str, is_running: bool) -> None:
        """Update the in-memory state and the status label for one service."""
        self.service_running[service_name] = is_running
        label = self.status_labels.get(service_name)
        if not label:
            return

        if is_running:
            label.configure(
                text="● Running", text_color=Palette.SERVICE_ACCENTS[service_name]
            )
        else:
            label.configure(text="● Idle", text_color=Palette.TEXT_3)

    def _start_all_sequence(self) -> None:
        """
        Launch all services sequentially in a background thread to prevent UI freezing.
        """

        def sequence() -> None:
            self.append_log("SYSTEM", "Initiating master launch sequence...")

            for service_name in SERVICES:
                self.managers[service_name].start()
                # Widget updates must happen on the main thread, so the status
                # label refresh is scheduled via `after` rather than called directly.
                self.after(0, self._set_service_running, service_name, True)
                time.sleep(1.0)

            self._open_client_ui()

        threading.Thread(target=sequence, daemon=True).start()

    def _stop_all(self) -> None:
        """Stop all running microservices."""
        for service_name, manager in self.managers.items():
            manager.stop()
            self._set_service_running(service_name, False)

    def _open_client_ui(self) -> None:
        """Open the frontend interface securely via the local HTTP server."""
        webbrowser.open("http://localhost:8000")
        self.append_log(
            "SYSTEM", "Client UI opened in default browser (http://localhost:8000)."
        )

    def _on_closing(self) -> None:
        """Handle the window close event to ensure child processes are terminated."""
        self.append_log("SYSTEM", "Shutting down processes safely. Please wait...")
        self._stop_all()
        self.destroy()


if __name__ == "__main__":
    app = SecureLauncherUI()
    app.mainloop()
