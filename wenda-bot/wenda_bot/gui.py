from __future__ import annotations

import json
import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import win32api
import win32con

from .main import load_config, run_bot_loop
from .win import find_windows_by_title_regex, get_client_size, get_cursor_pos, screen_to_client


class BotGui:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Wenda Bot Control Panel")
        self.root.geometry("1080x760")

        self.config_path = Path(__file__).resolve().parents[1] / "config.json"
        self.stop_event: threading.Event | None = None
        self.worker: threading.Thread | None = None
        self.capture_stop_event: threading.Event | None = None
        self.capture_worker: threading.Thread | None = None
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.matched_hwnds: list[int | None] = []

        self._build_ui()
        self._refresh_windows()
        self.root.after(120, self._drain_log_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text=f"Config: {self.config_path}").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(top, text="Refresh Windows", command=self._refresh_windows).pack(side=tk.LEFT, padx=4)
        self.start_btn = ttk.Button(top, text="Start Bot", command=self._start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=4)
        self.stop_btn = ttk.Button(top, text="Stop Bot", command=self._stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        self.status_var = tk.StringVar(value="Status: idle")
        ttk.Label(top, textvariable=self.status_var).pack(side=tk.RIGHT, padx=4)

        mid = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        mid.pack(fill=tk.BOTH, expand=False)

        ttk.Label(mid, text="Detected Window Mapping").pack(anchor=tk.W)
        self.mapping = tk.Text(mid, height=11, wrap=tk.NONE)
        self.mapping.pack(fill=tk.BOTH, expand=False, pady=(4, 0))
        self.mapping.configure(state=tk.DISABLED)

        calibrate = ttk.LabelFrame(self.root, text="Click Point Calibration", padding=(8, 6))
        calibrate.pack(fill=tk.X, padx=8, pady=(0, 8))

        row1 = ttk.Frame(calibrate)
        row1.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(row1, text="Client Slot").pack(side=tk.LEFT)
        self.client_slot_var = tk.StringVar(value="1")
        self.client_slot_box = ttk.Combobox(
            row1,
            textvariable=self.client_slot_var,
            values=["1", "2", "3", "4", "5"],
            width=5,
            state="readonly",
        )
        self.client_slot_box.pack(side=tk.LEFT, padx=(8, 14))

        ttk.Label(row1, text="Target Point").pack(side=tk.LEFT)
        self.target_point_var = tk.StringVar(value="npc")
        self.target_point_box = ttk.Combobox(
            row1,
            textvariable=self.target_point_var,
            values=["npc", "dialog_continue", "auto_battle"],
            width=18,
            state="readonly",
        )
        self.target_point_box.pack(side=tk.LEFT, padx=(8, 14))

        self.capture_btn = ttk.Button(row1, text="Start Capture (F8)", command=self._start_capture)
        self.capture_btn.pack(side=tk.LEFT, padx=4)
        self.capture_cancel_btn = ttk.Button(
            row1, text="Cancel Capture", command=self._cancel_capture, state=tk.DISABLED
        )
        self.capture_cancel_btn.pack(side=tk.LEFT, padx=4)

        self.capture_hint_var = tk.StringVar(
            value="Hint: click Start Capture, move mouse over game target, press F8 to save."
        )
        ttk.Label(calibrate, textvariable=self.capture_hint_var).pack(anchor=tk.W, pady=(4, 2))

        bottom = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        bottom.pack(fill=tk.BOTH, expand=True)

        ttk.Label(bottom, text="Runtime Logs").pack(anchor=tk.W)
        self.logs = tk.Text(bottom, wrap=tk.WORD)
        self.logs.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self.logs.configure(state=tk.DISABLED)

    def _set_mapping_text(self, text: str) -> None:
        self.mapping.configure(state=tk.NORMAL)
        self.mapping.delete("1.0", tk.END)
        self.mapping.insert(tk.END, text)
        self.mapping.configure(state=tk.DISABLED)

    def _append_log(self, line: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        self.logs.configure(state=tk.NORMAL)
        self.logs.insert(tk.END, f"[{stamp}] {line}\n")
        self.logs.see(tk.END)
        self.logs.configure(state=tk.DISABLED)

    def _refresh_windows(self) -> None:
        try:
            cfg = load_config(self.config_path)
            lines: list[str] = []
            self.matched_hwnds = []
            for idx, client in enumerate(cfg.clients):
                matches = find_windows_by_title_regex(client.title_regex)
                if len(matches) <= idx:
                    self.matched_hwnds.append(None)
                    lines.append(
                        f"{client.name}: regex={client.title_regex!r} | found={len(matches)} | target=NOT FOUND"
                    )
                else:
                    target = matches[idx]
                    self.matched_hwnds.append(target.hwnd)
                    lines.append(
                        f"{client.name}: regex={client.title_regex!r} | found={len(matches)} "
                        f"| target hwnd={target.hwnd} title={target.title!r}"
                    )
            self._set_mapping_text("\n".join(lines))
            self._append_log("window scan updated")
        except Exception as e:
            self._append_log(f"refresh failed: {e!r}")

    def _start_bot(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        try:
            cfg = load_config(self.config_path)
        except Exception as e:
            self._append_log(f"config load failed: {e!r}")
            return

        self.stop_event = threading.Event()
        self.worker = threading.Thread(
            target=run_bot_loop,
            args=(cfg, self.stop_event),
            kwargs={"log_fn": self.log_queue.put},
            daemon=True,
        )
        self.worker.start()
        self.status_var.set("Status: running")
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self._append_log("bot started")

    def _stop_bot(self) -> None:
        if self.stop_event is not None:
            self.stop_event.set()
        self.status_var.set("Status: idle")
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self._append_log("bot stop requested")

    def _start_capture(self) -> None:
        if self.worker and self.worker.is_alive():
            self._append_log("please stop bot before capture")
            return
        if self.capture_worker and self.capture_worker.is_alive():
            self._append_log("capture is already running")
            return

        self._refresh_windows()
        slot = int(self.client_slot_var.get()) - 1
        if slot < 0 or slot >= len(self.matched_hwnds):
            self._append_log("invalid client slot")
            return
        hwnd = self.matched_hwnds[slot]
        if not hwnd:
            self._append_log(f"client slot {slot+1} has no matched window")
            return
        target = self.target_point_var.get().strip()
        if target not in {"npc", "dialog_continue", "auto_battle"}:
            self._append_log(f"invalid target point: {target}")
            return

        self.capture_stop_event = threading.Event()
        self.capture_worker = threading.Thread(
            target=self._capture_worker_fn,
            args=(hwnd, target, slot + 1, self.capture_stop_event),
            daemon=True,
        )
        self.capture_worker.start()
        self.capture_btn.configure(state=tk.DISABLED)
        self.capture_cancel_btn.configure(state=tk.NORMAL)
        self.capture_hint_var.set(
            f"Capturing slot={slot+1} target={target}. Press F8 to save, Esc to cancel."
        )
        self._append_log(
            f"capture started: slot={slot+1} target={target}; move mouse over game window and press F8"
        )
        self.root.after(120, self._watch_capture_thread)

    def _cancel_capture(self) -> None:
        if self.capture_stop_event is not None:
            self.capture_stop_event.set()
        self._append_log("capture cancel requested")

    def _watch_capture_thread(self) -> None:
        if self.capture_worker and self.capture_worker.is_alive():
            self.root.after(120, self._watch_capture_thread)
            return
        self.capture_btn.configure(state=tk.NORMAL)
        self.capture_cancel_btn.configure(state=tk.DISABLED)
        self.capture_hint_var.set(
            "Hint: click Start Capture, move mouse over game target, press F8 to save."
        )

    def _capture_worker_fn(
        self, hwnd: int, target: str, slot_label: int, stop_event: threading.Event
    ) -> None:
        # Poll keyboard globally. F8 commits current mouse point; ESC cancels.
        while not stop_event.is_set():
            if win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 1:
                self.log_queue.put("capture cancelled (Esc)")
                return
            if win32api.GetAsyncKeyState(win32con.VK_F8) & 1:
                sx, sy = get_cursor_pos()
                cx, cy = screen_to_client(hwnd, sx, sy)
                w, h = get_client_size(hwnd)
                if cx < 0 or cy < 0 or cx >= w or cy >= h:
                    self.log_queue.put(
                        f"capture ignored: point ({cx},{cy}) out of slot {slot_label} client bounds ({w}x{h})"
                    )
                    return
                self._save_click_point(target=target, x=cx, y=cy)
                self.log_queue.put(
                    f"saved clicks.{target}=({cx},{cy}) for slot {slot_label} reference (config is global)"
                )
                return
            time.sleep(0.03)

    def _save_click_point(self, target: str, x: int, y: int) -> None:
        raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        clicks = raw.setdefault("clicks", {})
        clicks[target] = {"x": int(x), "y": int(y)}
        self.config_path.write_text(
            json.dumps(raw, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _drain_log_queue(self) -> None:
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self._append_log(msg)
        except queue.Empty:
            pass
        self.root.after(120, self._drain_log_queue)

    def _on_close(self) -> None:
        self._stop_bot()
        self._cancel_capture()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    BotGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()

