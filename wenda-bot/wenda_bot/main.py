from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Event
from typing import Callable, Optional

from .capture import Rect, grab_client, crop
from .input import click_client
from .ocr import OcrConfig, OcrEngine
from .win import find_windows_by_title_regex


@dataclass
class ClientConfig:
    name: str
    title_regex: str


@dataclass
class BotConfig:
    poll_interval_ms: int
    focus_delay_ms: int
    after_click_delay_ms: int
    clients: list[ClientConfig]
    dialog_region: Rect
    quest_region: Rect
    click_npc: tuple[int, int]
    click_dialog_continue: tuple[int, int]
    click_auto_battle: tuple[int, int]
    ocr: OcrConfig


LogFn = Callable[[str], None]


def load_config(path: Path) -> BotConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    clients = [
        ClientConfig(name=w.get("name", f"client{i+1}"), title_regex=w["title_regex"])
        for i, w in enumerate(raw["windows"])
    ]

    def rect_of(key: str) -> Rect:
        r = raw["regions"][key]
        return Rect(x=int(r["x"]), y=int(r["y"]), w=int(r["w"]), h=int(r["h"]))

    def xy_of(key: str) -> tuple[int, int]:
        c = raw["clicks"][key]
        return int(c["x"]), int(c["y"])

    o = raw["ocr"]
    ocr_cfg = OcrConfig(
        backend=str(o.get("backend", "auto")),
        tesseract_cmd=str(o["tesseract_cmd"]),
        lang=str(o.get("lang", "chi_sim")),
        psm=int(o.get("psm", 6)),
    )

    return BotConfig(
        poll_interval_ms=int(raw.get("poll_interval_ms", 450)),
        focus_delay_ms=int(raw.get("focus_delay_ms", 120)),
        after_click_delay_ms=int(raw.get("after_click_delay_ms", 120)),
        clients=clients,
        dialog_region=rect_of("dialog"),
        quest_region=rect_of("quest_hint"),
        click_npc=xy_of("npc"),
        click_dialog_continue=xy_of("dialog_continue"),
        click_auto_battle=xy_of("auto_battle"),
        ocr=ocr_cfg,
    )


def pick_nth_window(title_regex: str, n: int) -> Optional[int]:
    matches = find_windows_by_title_regex(title_regex)
    if len(matches) <= n:
        return None
    return matches[n].hwnd


def scan_windows(cfg: BotConfig, log_fn: LogFn = print) -> None:
    for idx, client in enumerate(cfg.clients):
        matches = find_windows_by_title_regex(client.title_regex)
        log_fn(
            f"[scan] {client.name} regex={client.title_regex!r} "
            f"found={len(matches)} target_index={idx}"
        )


def run_bot_loop(cfg: BotConfig, stop_event: Event, log_fn: LogFn = print) -> None:
    ocr_engine = OcrEngine(cfg.ocr)
    log_fn(f"ocr backend: {ocr_engine.backend}")
    if not ocr_engine.is_enabled:
        log_fn(
            "OCR is disabled (no backend available).\n"
            "- Install rapidocr-onnxruntime (recommended)\n"
            "- or install Tesseract and set ocr.tesseract_cmd in config.json\n"
            "- bot will continue without text recognition\n"
        )

    scan_windows(cfg, log_fn=log_fn)

    def do_click(client_name: str, hwnd: int, tag: str, xy: tuple[int, int]) -> None:
        try:
            click_client(hwnd, *xy, focus=True)
        except Exception as e:
            log_fn(f"[{client_name}] {tag} click skipped: {e}")
            return

    while not stop_event.is_set():
        for idx, client in enumerate(cfg.clients):
            if stop_event.is_set():
                break
            hwnd = pick_nth_window(client.title_regex, idx)
            if not hwnd:
                log_fn(f"[{client.name}] window not found for regex={client.title_regex!r} (index {idx})")
                continue

            try:
                # 1) Read dialog / quest hint text
                img = grab_client(hwnd)
                dialog_img = crop(img, cfg.dialog_region)
                quest_img = crop(img, cfg.quest_region)
                dialog_text = ocr_engine.image_to_text(dialog_img)
                quest_text = ocr_engine.image_to_text(quest_img)

                if dialog_text or quest_text:
                    log_fn(f"[{client.name}] dialog={dialog_text[:80]!r} quest={quest_text[:80]!r}")

                # 2) Very simple demo actions (placeholder for state machine)
                # Try click NPC, then click continue, then enable auto battle.
                do_click(client.name, hwnd, "npc", cfg.click_npc)
                time.sleep(cfg.after_click_delay_ms / 1000.0)
                do_click(client.name, hwnd, "dialog_continue", cfg.click_dialog_continue)
                time.sleep(cfg.after_click_delay_ms / 1000.0)
                do_click(client.name, hwnd, "auto_battle", cfg.click_auto_battle)
                time.sleep(cfg.after_click_delay_ms / 1000.0)
            except Exception as e:
                log_fn(f"[{client.name}] error: {e!r}")

            time.sleep(cfg.poll_interval_ms / 1000.0)


def main() -> None:
    config_path = Path(__file__).resolve().parents[1] / "config.json"
    cfg = load_config(config_path)
    print("wenda-bot starting...")
    print(f"config: {config_path}")
    stop_event = Event()
    try:
        run_bot_loop(cfg, stop_event=stop_event, log_fn=print)
    except KeyboardInterrupt:
        stop_event.set()
        print("stopped by keyboard interrupt")


if __name__ == "__main__":
    main()

