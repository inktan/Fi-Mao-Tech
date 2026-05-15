from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import mss

from .win import get_client_rect


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int


def grab_client(hwnd: int) -> np.ndarray:
    left, top, right, bottom = get_client_rect(hwnd)
    w = max(1, right - left)
    h = max(1, bottom - top)
    with mss.mss() as sct:
        img = np.array(sct.grab({"left": left, "top": top, "width": w, "height": h}))
    # mss returns BGRA
    return img[:, :, :3].copy()


def crop(img_bgr: np.ndarray, rect: Rect) -> np.ndarray:
    h, w = img_bgr.shape[:2]
    x1 = max(0, rect.x)
    y1 = max(0, rect.y)
    x2 = min(w, rect.x + rect.w)
    y2 = min(h, rect.y + rect.h)
    if x2 <= x1 or y2 <= y1:
        return img_bgr[0:1, 0:1].copy()
    return img_bgr[y1:y2, x1:x2].copy()

