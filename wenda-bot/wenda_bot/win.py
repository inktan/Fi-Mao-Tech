from __future__ import annotations

from dataclasses import dataclass
import re

import win32con
import win32gui
import win32process


@dataclass(frozen=True)
class WindowInfo:
    hwnd: int
    title: str
    pid: int


def _is_visible_window(hwnd: int) -> bool:
    if not win32gui.IsWindow(hwnd):
        return False
    if not win32gui.IsWindowVisible(hwnd):
        return False
    title = win32gui.GetWindowText(hwnd) or ""
    return bool(title.strip())


def list_windows() -> list[WindowInfo]:
    results: list[WindowInfo] = []

    def enum_handler(hwnd: int, _):
        if not _is_visible_window(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        results.append(WindowInfo(hwnd=hwnd, title=title, pid=pid))

    win32gui.EnumWindows(enum_handler, None)
    return results


def find_windows_by_title_regex(title_regex: str) -> list[WindowInfo]:
    rx = re.compile(title_regex)
    return [w for w in list_windows() if rx.search(w.title)]


def focus_window(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        # Some windows need a nudge; fall back to bring-to-top.
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetForegroundWindow(hwnd)


def get_client_rect(hwnd: int) -> tuple[int, int, int, int]:
    # Returns (left, top, right, bottom) in screen coords for client area.
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    pt_left_top = win32gui.ClientToScreen(hwnd, (left, top))
    pt_right_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
    return pt_left_top[0], pt_left_top[1], pt_right_bottom[0], pt_right_bottom[1]


def get_client_size(hwnd: int) -> tuple[int, int]:
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    return max(0, right - left), max(0, bottom - top)


def client_to_screen(hwnd: int, x: int, y: int) -> tuple[int, int]:
    return win32gui.ClientToScreen(hwnd, (x, y))


def screen_to_client(hwnd: int, x: int, y: int) -> tuple[int, int]:
    return win32gui.ScreenToClient(hwnd, (x, y))


def get_cursor_pos() -> tuple[int, int]:
    return win32gui.GetCursorPos()

