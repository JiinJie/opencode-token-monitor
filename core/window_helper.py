# -*- coding: utf-8 -*-
"""
Windows native window inspection and foreground focus capture module.
"""

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import Optional
import psutil

# Windows API dynamic library
user32 = ctypes.windll.user32


@dataclass
class ForegroundInfo:
    """Metadata representing the current foreground window."""
    hwnd: int
    pid: int
    process: str
    title: str

    @property
    def is_opencode(self) -> bool:
        """Determine whether the current foreground window belongs to OpenCode."""
        p = self.process.lower()
        t = self.title.lower()
        return "opencode" in p or "opencode" in t


class WindowHelper:
    """Windows native window detection helper."""

    @staticmethod
    def get_foreground_info() -> Optional[ForegroundInfo]:
        """Retrieve information about the top-level window currently holding system focus."""
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1) if length > 0 else None
        title = ""
        if buff:
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value

        pname = ""
        try:
            pname = psutil.Process(pid.value).name().lower()
        except Exception:
            pass

        return ForegroundInfo(
            hwnd=hwnd,
            pid=pid.value,
            process=pname,
            title=title
        )
