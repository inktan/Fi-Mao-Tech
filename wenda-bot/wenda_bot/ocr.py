from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pytesseract

try:
    from rapidocr_onnxruntime import RapidOCR
except Exception:
    RapidOCR = None


@dataclass(frozen=True)
class OcrConfig:
    backend: str = "auto"
    tesseract_cmd: str = ""
    lang: str = "chi_sim"
    psm: int = 6


def _preprocess_for_ocr(img_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th


class OcrEngine:
    def __init__(self, cfg: OcrConfig):
        self.cfg = cfg
        self.backend = "none"
        self._rapid = None

        request = (cfg.backend or "auto").lower().strip()
        if request in {"auto", "rapidocr"} and RapidOCR is not None:
            self._rapid = RapidOCR()
            self.backend = "rapidocr"
            return

        if request in {"auto", "tesseract"} and Path(cfg.tesseract_cmd).exists():
            self.backend = "tesseract"
            return

    @property
    def is_enabled(self) -> bool:
        return self.backend != "none"

    def image_to_text(self, img_bgr: np.ndarray) -> str:
        if self.backend == "none":
            return ""

        proc = _preprocess_for_ocr(img_bgr)

        if self.backend == "rapidocr":
            result, _ = self._rapid(proc)
            if not result:
                return ""
            # result item: [box, text, score]
            return "\n".join([str(item[1]).strip() for item in result if len(item) >= 2]).strip()

        pytesseract.pytesseract.tesseract_cmd = self.cfg.tesseract_cmd
        config = f"--psm {int(self.cfg.psm)}"
        text = pytesseract.image_to_string(proc, lang=self.cfg.lang, config=config) or ""
        return text.replace("\x0c", "").strip()

