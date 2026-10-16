# -*- coding: utf-8 -*-
"""
Data models and domain entity definitions.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .window_helper import ForegroundInfo


@dataclass
class SessionMetrics:
    """Telemetry and throughput metrics data model for a single session."""
    session_id: str
    title: str
    directory: str
    dir_name: str
    parent_id: Optional[str]
    model: str

    # State phase flags
    is_waiting_ttft: bool = False
    is_generating: bool = False
    is_burst: bool = False

    # Throughput metrics (tokens/s)
    tps: float = 0.0               # Current displayed rate (adaptive anti-burst rate)
    effective_tps: float = 0.0     # End-to-end human-perceived throughput (including TTFT)
    decode_tps: float = 0.0        # Pure streaming decode generation throughput

    # Timing metrics (seconds)
    ttft_s: float = 0.0            # Time To First Token (TTFT)
    decode_s: float = 0.0          # Decode / generation phase duration
    total_s: float = 0.0           # Total elapsed duration for this round

    # Token counts and statistics
    total_out: int = 0             # Total output tokens
    in_tok: int = 0                # Input prompt tokens
    out_tok: int = 0               # Output completion tokens
    reas_tok: int = 0              # Thinking / reasoning tokens
    cache_read: int = 0            # Cache read tokens
    cost: float = 0.0              # Estimated cost ($)
    time_updated: int = 0          # Updated timestamp (ms)

    # Detailed hover text
    tooltip: str = ""


@dataclass
class MonitorState:
    """Snapshot representing a single polling refresh cycle of the monitor."""
    db_exists: bool
    is_opencode_foreground: bool
    foreground_info: Optional[ForegroundInfo]
    foreground_session: Optional[SessionMetrics]
    other_sessions: List[SessionMetrics] = field(default_factory=list)
    raw_session_count: int = 0
