from __future__ import annotations

import time

import pydirectinput

from .win import client_to_screen, focus_window, get_client_size


def click_client(hwnd: int, x: int, y: int, focus: bool = True) -> None:
    w, h = get_client_size(hwnd)
    if w <= 0 or h <= 0:
        raise ValueError(f"invalid client size: {(w, h)}")
    if x < 0 or y < 0 or x >= w or y >= h:
        raise ValueError(f"click out of client bounds: ({x}, {y}) not in [0,{w})x[0,{h})")

    if focus:
        focus_window(hwnd)
        time.sleep(0.05)
    sx, sy = client_to_screen(hwnd, x, y)
    pydirectinput.moveTo(sx, sy)
    time.sleep(0.03)
    pydirectinput.click()

