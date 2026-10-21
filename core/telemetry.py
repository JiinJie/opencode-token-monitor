# -*- coding: utf-8 -*-
"""
OpenCode SQLite WAL Telemetry Data Collection and Throughput Analysis Engine.
Decoupled from any GUI framework; supports CLI console execution or embedding into external tools.
"""

import os
import json
import sqlite3
import time
from typing import List, Optional

from .config import (
    DEFAULT_DB_PATH,
    BURST_DECODE_THRESHOLD_S,
    BURST_MIN_TOKENS,
    BURST_RATIO_THRESHOLD,
    BURST_MIN_TOTAL_S,
)
from .window_helper import WindowHelper, ForegroundInfo
from .models import SessionMetrics, MonitorState


class OpenCodeTelemetry:
    """OpenCode Telemetry Collector."""

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        enable_anti_burst: bool = True,
        enable_ttft: bool = True
    ):
        self.db_path = db_path
        self.enable_anti_burst = enable_anti_burst
        self.enable_ttft = enable_ttft

    def collect(self) -> MonitorState:
        """
        Collect a full telemetry snapshot and return the domain state model.
        """
        if not os.path.exists(self.db_path):
            return MonitorState(
                db_exists=False,
                is_opencode_foreground=False,
                foreground_info=None,
                foreground_session=None,
                other_sessions=[]
            )

        # 1. Inspect foreground window focus
        fg_info: Optional[ForegroundInfo] = WindowHelper.get_foreground_info()
        is_opencode_fg = fg_info.is_opencode if fg_info else False
        fg_title = fg_info.title if fg_info else ""

        # 2. Query recent active sessions from SQLite WAL
        session_data_list = self._query_active_sessions()

        if not session_data_list:
            return MonitorState(
                db_exists=True,
                is_opencode_foreground=is_opencode_fg,
                foreground_info=fg_info,
                foreground_session=None,
                other_sessions=[]
            )

        # 3. Match foreground session (prioritize project/directory name in title)
        fg_session: Optional[SessionMetrics] = None
        if is_opencode_fg and fg_title:
            for s in session_data_list:
                if (s.dir_name.lower() in fg_title.lower()) or (s.title and s.title.lower() in fg_title.lower()):
                    fg_session = s
                    break

        if not fg_session:
            fg_session = session_data_list[0]

        # 4. Remaining sessions (background candidates)
        other_sessions = [s for s in session_data_list if s.session_id != fg_session.session_id]

        return MonitorState(
            db_exists=True,
            is_opencode_foreground=is_opencode_fg,
            foreground_info=fg_info,
            foreground_session=fg_session,
            other_sessions=other_sessions,
            raw_session_count=len(session_data_list)
        )

    def _query_active_sessions(self) -> List[SessionMetrics]:
        """Connect to SQLite WAL in read-only mode for non-blocking analysis."""
        results: List[SessionMetrics] = []
        now_ms = time.time() * 1000

        try:
            # Open SQLite in read-only URI mode to guarantee zero write locks and zero conflicts
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cur = conn.cursor()

            cur.execute("""
                SELECT id, title, directory, parent_id, time_updated
                FROM session
                ORDER BY time_updated DESC
                LIMIT 15
            """)
            sessions = cur.fetchall()

            for ses in sessions:
                ses_id, title, directory, parent_id, s_tu = ses
                dir_name = os.path.basename((directory or "").rstrip('/\\')) or "OpenCode"

                # Query the latest assistant message in the session
                cur.execute("""
                    SELECT id, time_created, time_updated, data
                    FROM message
                    WHERE session_id = ? AND json_extract(data, '$.role') = 'assistant'
                    ORDER BY time_created DESC
                    LIMIT 1
                """, (ses_id,))
                msg_row = cur.fetchone()
                if not msg_row:
                    continue

                msg_id, m_tc, m_tu, data_raw = msg_row
                data = json.loads(data_raw)
                t_info = data.get("time", {})
                tokens = data.get("tokens", {})

                out_tok = tokens.get("output", 0)
                reas_tok = tokens.get("reasoning", 0)
                in_tok = tokens.get("input", 0)
                cache_read = tokens.get("cache", {}).get("read", 0)
                cost = data.get("cost", 0.0)
                model = data.get("modelID", "Model")

                c_ms = t_info.get("completed")
                cr_ms = t_info.get("created") or m_tc

                # Query step start timestamp (step-start)
                cur.execute("""
                    SELECT time_created FROM part
                    WHERE message_id = ? AND json_extract(data, '$.type') = 'step-start'
                    ORDER BY time_created DESC LIMIT 1
                """, (msg_id,))
                step_start_row = cur.fetchone()
                step_start_ms = step_start_row[0] if step_start_row else cr_ms

                # Query text and reasoning stream parts
                cur.execute("""
                    SELECT time_created, json_extract(data, '$.time.start'), json_extract(data, '$.text')
                    FROM part
                    WHERE message_id = ? AND json_extract(data, '$.type') IN ('reasoning', 'text')
                    ORDER BY time_created ASC
                """, (msg_id,))
                parts_data = cur.fetchall()

                total_chars = sum(len(p[2] or "") for p in parts_data)
                total_out = out_tok + reas_tok

                is_waiting_ttft = False
                is_generating = False
                is_burst = False
                tps = 0.0
                effective_tps = 0.0
                decode_tps = 0.0
                ttft_s = 0.0
                decode_s = 0.0
                total_s = 0.0

                if not c_ms:
                    # Request in progress (completed timestamp not yet recorded)
                    if self.enable_ttft and (not parts_data or total_chars == 0):
                        # Phase 1: Waiting for first token from server (TTFT stage)
                        is_waiting_ttft = True
                        ttft_s = max(0.1, (now_ms - step_start_ms) / 1000.0)
                    else:
                        # Phase 2: Active streaming decoding
                        is_generating = True
                        first_tok_ms = parts_data[0][1] or parts_data[0][0] if parts_data else step_start_ms
                        ttft_s = max(0.01, (first_tok_ms - step_start_ms) / 1000.0)
                        decode_s = max(0.1, (now_ms - first_tok_ms) / 1000.0)
                        total_s = max(0.1, (now_ms - step_start_ms) / 1000.0)
                        est_tok = max(total_out, total_chars * 0.5)
                        decode_tps = est_tok / decode_s
                        effective_tps = est_tok / total_s
                        tps = decode_tps
                else:
                    # Phase 3: Round finished
                    if parts_data:
                        first_tok_ms = parts_data[0][1] or parts_data[0][0]
                        ttft_s = max(0.01, (first_tok_ms - step_start_ms) / 1000.0)
                        decode_s = max(0.01, (c_ms - first_tok_ms) / 1000.0)
                        total_s = max(0.01, (c_ms - step_start_ms) / 1000.0)
                    else:
                        total_s = max(0.01, (c_ms - step_start_ms) / 1000.0)
                        decode_s = total_s
                        ttft_s = 0.0

                    effective_tps = total_out / max(0.01, total_s)
                    decode_tps = total_out / max(0.01, decode_s)

                    # Anti-Burst Detection:
                    # Conditions: extremely fast transfer with many tokens, or long total time with very low decode ratio
                    if self.enable_anti_burst and (
                        (decode_s < BURST_DECODE_THRESHOLD_S and total_out > BURST_MIN_TOKENS) or \
                        (total_s > BURST_MIN_TOTAL_S and (decode_s / total_s) < BURST_RATIO_THRESHOLD)
                    ):
                        is_burst = True
                        tps = effective_tps  # Fallback to end-to-end human-perceived throughput
                    else:
                        is_burst = False
                        tps = decode_tps    # Use pure decoding streaming throughput

                burst_desc = "检测到服务端缓冲积压/整包推送 (已按真实体感速率校准)" if is_burst else "正常流式传输"
                tooltip = (
                    f"【会话】 {title or dir_name}\n"
                    f"【路径】 {directory}\n"
                    f"【模型】 {model}\n"
                    f"----------------------------------------\n"
                    f"【端到端体感速率】 {effective_tps:.1f} tokens/s (含全部等待)\n"
                    f"【纯解码吐字吞吐】 {decode_tps:.1f} tokens/s (瞬时传输)\n"
                    f"【传输模式】 {burst_desc}\n"
                    f"----------------------------------------\n"
                    f"【首字延迟 TTFT】 {ttft_s:.2f} 秒\n"
                    f"【解码传输耗时】 {decode_s:.2f} 秒\n"
                    f"【本次交互耗时】 {total_s:.2f} 秒\n"
                    f"【输出 Token】 {out_tok} (思考过程: {reas_tok})\n"
                    f"【输入 Token】 {in_tok} (缓存读取: {cache_read})\n"
                    f"【费用】 ${cost:.5f}\n"
                    f"【类型】 {'子任务 Subagent' if parent_id else '主会话 Primary'}"
                )

                metric = SessionMetrics(
                    session_id=ses_id,
                    title=title or "",
                    directory=directory or "",
                    dir_name=dir_name,
                    parent_id=parent_id,
                    model=model,
                    is_waiting_ttft=is_waiting_ttft,
                    is_generating=is_generating,
                    is_burst=is_burst,
                    tps=tps,
                    effective_tps=effective_tps,
                    decode_tps=decode_tps,
                    ttft_s=ttft_s,
                    decode_s=decode_s,
                    total_s=total_s,
                    total_out=total_out,
                    in_tok=in_tok,
                    out_tok=out_tok,
                    reas_tok=reas_tok,
                    cache_read=cache_read,
                    cost=cost,
                    time_updated=m_tu or s_tu or 0,
                    tooltip=tooltip
                )
                results.append(metric)

            conn.close()
        except Exception as e:
            # Silent protection to avoid crashing external consumers
            pass

        return results


if __name__ == "__main__":
    # CLI standalone test mode
    import sys
    telemetry = OpenCodeTelemetry()
    state = telemetry.collect()
    print("=== OpenCode Telemetry CLI Monitor ===")
    print(f"DB Exists: {state.db_exists}")
    print(f"OpenCode Foreground: {state.is_opencode_foreground}")
    if state.foreground_info:
        print(f"Active App: {state.foreground_info.process} ({state.foreground_info.title})")
    if state.foreground_session:
        fg = state.foreground_session
        print(f"[FG] {fg.dir_name} | {fg.tps:.1f} tok/s | {fg.model} | {fg.total_out} tok")
    for i, s in enumerate(state.other_sessions[:2]):
        print(f"[BG {i+1}] {s.dir_name} | {s.tps:.1f} tok/s | {s.model}")
