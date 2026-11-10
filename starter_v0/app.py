from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
import yaml

APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from chat import (  # noqa: E402
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env  # noqa: E402
from providers import make_provider  # noqa: E402
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import ArtifactVersion, artifact_version_dict, build_artifact_version, short_hash  # noqa: E402

ARTIFACTS_DIR = APP_ROOT / "artifacts"
TRANSCRIPTS_DIR = APP_ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_YAML_PATH = ARTIFACTS_DIR / "tools.yaml"
VERSION_LOG_PATH = ARTIFACTS_DIR / "version_log.csv"

PROVIDER_CONFIGS: dict[str, dict[str, str | None]] = {
    "openai": {"label": "OpenAI", "env": "OPENAI_API_KEY", "default_model": "gpt-4o-mini"},
    "openrouter": {"label": "OpenRouter", "env": "OPENROUTER_API_KEY", "default_model": "openai/gpt-4o-mini"},
    "gemini": {"label": "Google Gemini", "env": "GEMINI_API_KEY", "default_model": "gemini-2.5-flash"},
    "anthropic": {"label": "Anthropic Claude", "env": "ANTHROPIC_API_KEY", "default_model": "claude-haiku-4-5-20251001"},
    "ollama": {"label": "Ollama (Local)", "env": None, "default_model": "qwen2.5:7b"},
}

TOOL_ENV_KEYS: list[tuple[str, str, bool]] = [
    ("TAVILY_API_KEY", "lookup (Web Search)", True),
    ("FIRECRAWL_API_KEY", "fetch (Read URL)", True),
    ("RAPIDAPI_KEY", "timeline / social_search", True),
    ("TELEGRAM_BOT_TOKEN", "send (Telegram bonus)", False),
    ("TELEGRAM_CHAT_ID", "send (Telegram chat ID)", False),
]

SAMPLE_PROMPTS: list[tuple[str, str]] = [
    ("📰 Tin AI hôm nay", "Tin tức AI hôm nay có gì nổi bật?"),
    ("🐦 Tweet Elon Musk", "Lấy 5 tweet mới nhất của Elon Musk"),
    ("❓ Test Clarify (thiếu @)", "Tóm tắt 5 tweet mới nhất giúp mình"),
    ("📨 Test Send (xác nhận)", "Đăng bản tin này lên Telegram giúp mình"),
    ("📄 Tìm paper arXiv", "Tìm 3 paper mới nhất trên arXiv về AI agents"),
    ("📚 Verify DOI (Crossref)", "Kiểm tra DOI 10.1038/s41586-021-03819-2 trên Crossref giúp mình"),
    ("🚫 Test ngoài phạm vi", "Giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?"),
]


def load_runtime_env() -> None:
    load_lab_env(APP_ROOT)
    # Fallback for cloud deployments (e.g. Streamlit Community Cloud) using st.secrets.
    secrets_candidates = (
        APP_ROOT / ".streamlit" / "secrets.toml",
        APP_ROOT.parent / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
    )
    if any(candidate.exists() for candidate in secrets_candidates):
        try:
            for key, value in st.secrets.items():
                if isinstance(value, str) and value and not os.getenv(key):
                    os.environ[key] = value
        except Exception:
            pass


def detect_default_provider() -> str:
    for provider_name in ("openai", "openrouter", "anthropic", "gemini", "ollama"):
        env_name = PROVIDER_CONFIGS[provider_name]["env"]
        if env_name is None or os.getenv(env_name):
            return provider_name
    return "openai"


def _sha256_variants(raw: bytes) -> set[str]:
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    variants: set[str] = set()
    for blob in (raw, lf, crlf):
        digest = hashlib.sha256(blob).hexdigest()
        variants.add(digest)
        variants.add(digest[:12])
    return variants


def read_version_log() -> list[dict[str, str]]:
    if not VERSION_LOG_PATH.exists():
        return []
    try:
        with VERSION_LOG_PATH.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except Exception:
        return []


def match_logged_version(
    prompt_bytes: bytes,
    tools_bytes: bytes,
    log_rows: list[dict[str, str]],
) -> dict[str, str] | None:
    p_variants = _sha256_variants(prompt_bytes)
    t_variants = _sha256_variants(tools_bytes)
    for row in reversed(log_rows):
        p_hash = (row.get("prompt_hash") or "").strip()
        t_hash = (row.get("tools_hash") or "").strip()
        if p_hash and t_hash and p_hash in p_variants and t_hash in t_variants:
            return row
    return None


@st.cache_data(ttl=15, show_spinner=False)
def discover_git_snapshots() -> list[dict[str, Any]]:
    log_rows = read_version_log()
    snapshots: list[dict[str, Any]] = []
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if top.returncode != 0 or not top.stdout.strip():
            return []
        git_root = Path(top.stdout.strip()).resolve()
        rel_prompt = SYSTEM_PROMPT_PATH.resolve().relative_to(git_root).as_posix()
        rel_tools = TOOLS_YAML_PATH.resolve().relative_to(git_root).as_posix()
        git_log = subprocess.run(
            ["git", "log", "--format=%H\t%s", "-n", "30", "--", rel_prompt, rel_tools],
            cwd=str(git_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
            check=False,
        )
        if git_log.returncode != 0:
            return []

        seen_lf_pairs: set[tuple[str, str]] = set()
        for line in git_log.stdout.splitlines():
            if "\t" not in line:
                continue
            commit_sha, subject = line.split("\t", 1)
            p_proc = subprocess.run(
                ["git", "show", f"{commit_sha}:{rel_prompt}"],
                cwd=str(git_root),
                capture_output=True,
                timeout=3,
                check=False,
            )
            t_proc = subprocess.run(
                ["git", "show", f"{commit_sha}:{rel_tools}"],
                cwd=str(git_root),
                capture_output=True,
                timeout=3,
                check=False,
            )
            if p_proc.returncode != 0 or t_proc.returncode != 0:
                continue

            p_bytes = p_proc.stdout
            t_bytes = t_proc.stdout
            lf_pair = (
                hashlib.sha256(p_bytes.replace(b"\r\n", b"\n")).hexdigest(),
                hashlib.sha256(t_bytes.replace(b"\r\n", b"\n")).hexdigest(),
            )
            if lf_pair in seen_lf_pairs:
                continue
            seen_lf_pairs.add(lf_pair)

            matched_log = match_logged_version(p_bytes, t_bytes, log_rows)
            ver_match = re.match(r"^(v\d+(?:[-_a-zA-Z0-9]*)?)\b", subject.strip(), re.IGNORECASE)
            if not matched_log and not ver_match:
                continue

            version_name = (matched_log.get("version") or "").strip() if matched_log else ""
            if not version_name and ver_match:
                version_name = ver_match.group(1)

            note = (
                (matched_log.get("changed_artifact") or "").strip()
                if matched_log
                else subject.strip()
            )
            reason = (matched_log.get("reason") or subject.strip()) if matched_log else subject.strip()
            snapshots.append(
                {
                    "key": f"git:{commit_sha[:12]}",
                    "version": version_name or commit_sha[:7],
                    "label": f"{version_name} — {note or subject.strip()} ({commit_sha[:7]})",
                    "commit": commit_sha,
                    "short_commit": commit_sha[:7],
                    "subject": subject.strip(),
                    "note": reason,
                    "prompt_text": p_bytes.decode("utf-8", errors="replace"),
                    "tools_yaml_text": t_bytes.decode("utf-8", errors="replace"),
                    "prompt_bytes": p_bytes,
                    "tools_bytes": t_bytes,
                }
            )
    except Exception:
        return []
    return snapshots


def build_snapshot_catalog() -> dict[str, dict[str, Any]]:
    log_rows = read_version_log()
    disk_prompt = SYSTEM_PROMPT_PATH.read_bytes()
    disk_tools = TOOLS_YAML_PATH.read_bytes()
    disk_match = match_logged_version(disk_prompt, disk_tools, log_rows)
    disk_ver = (disk_match.get("version") or "").strip() if disk_match else ""
    current_ver = disk_ver or "draft"
    current_label = f"Current (trên đĩa — đang là {disk_ver})" if disk_ver else "Current (trên đĩa — bản sửa cục bộ)"
    current_note = (
        (disk_match.get("reason") or f"Khớp {disk_ver} trên đĩa")
        if disk_match
        else "Đọc trực tiếp starter_v0/artifacts/system_prompt.md & tools.yaml trên đĩa"
    )
    catalog: dict[str, dict[str, Any]] = {
        "current": {
            "key": "current",
            "version": current_ver,
            "label": current_label,
            "commit": None,
            "short_commit": None,
            "note": current_note,
        }
    }
    for snap in discover_git_snapshots():
        catalog[snap["key"]] = snap
    return catalog


def load_runtime_artifacts(
    version_label: str,
    snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if snapshot is None or snapshot.get("key") == "current":
        system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        tool_declarations = load_tool_declarations(TOOLS_YAML_PATH)
        artifact_ver = build_artifact_version(version_label.strip() or "current", SYSTEM_PROMPT_PATH, TOOLS_YAML_PATH)
    else:
        system_prompt = snapshot["prompt_text"]
        parsed_tools = yaml.safe_load(snapshot["tools_yaml_text"]) or {}
        tool_declarations = list(parsed_tools["tools"])
        prompt_hash = hashlib.sha256(snapshot["prompt_bytes"]).hexdigest()
        tools_hash = hashlib.sha256(snapshot["tools_bytes"]).hexdigest()
        effective_ver = (version_label.strip() or snapshot["version"]).strip()
        artifact_ver = ArtifactVersion(
            version=effective_ver,
            artifact_version=f"{effective_ver}+p{short_hash(prompt_hash)}+t{short_hash(tools_hash)}",
            prompt_hash=prompt_hash,
            tools_hash=tools_hash,
        )

    openai_tools = to_openai_tools(tool_declarations)
    declared_names = [item["name"] for item in tool_declarations]
    missing_impls = [name for name in declared_names if name not in TOOL_FUNCTIONS]
    unregistered_impls = sorted(set(TOOL_FUNCTIONS) - set(declared_names))
    return {
        "system_prompt": system_prompt,
        "tool_declarations": tool_declarations,
        "openai_tools": openai_tools,
        "artifact_version": artifact_ver,
        "missing_impls": missing_impls,
        "unregistered_impls": unregistered_impls,
        "snapshot_commit": snapshot.get("commit") if snapshot else None,
    }


def extract_turn_diagnostics(turn: dict[str, Any]) -> dict[str, Any]:
    tool_errors: list[dict[str, str]] = []
    needs_confirmation: list[str] = []
    untrusted_notices: list[str] = []
    clarify_info: dict[str, Any] | None = None

    for event in turn.get("tool_events") or []:
        tool_name = str(event.get("tool") or "unknown")
        if event.get("error"):
            tool_errors.append({
                "tool": tool_name,
                "error": str(event.get("error")),
                "message": str(event.get("message") or event.get("error")),
            })
            continue

        result = event.get("result")
        if not isinstance(result, dict):
            continue

        if result.get("error") or result.get("status") in {"error", "provider_error"}:
            tool_errors.append({
                "tool": tool_name,
                "error": str(result.get("error") or result.get("status")),
                "message": str(result.get("message") or result.get("error") or "Tool failed"),
            })

        if result.get("status") == "needs_confirmation":
            needs_confirmation.append(
                str(result.get("message") or "Hành động này cần người dùng xác nhận rõ ràng trước khi thực hiện.")
            )

        if result.get("awaiting_user"):
            clarify_info = {
                "question": str(result.get("question") or turn.get("assistant_text") or ""),
                "response_type": str(result.get("response_type") or "text"),
                "options": list(result.get("options") or []),
            }

        if result.get("untrusted_text"):
            untrusted_notices.append(f"Tool `{tool_name}` đã tách nội dung đáng ngờ vào `untrusted_text`.")
        for item in result.get("results") or []:
            if isinstance(item, dict) and item.get("untrusted_text"):
                untrusted_notices.append(
                    f"Mục `{item.get('title') or item.get('section')}` có nội dung bị cách ly trong `untrusted_text`."
                )

    return {
        "provider_error": turn.get("error") if turn.get("status") == "provider_error" else None,
        "tool_errors": tool_errors,
        "needs_confirmation": needs_confirmation,
        "clarify_info": clarify_info,
        "untrusted_notices": untrusted_notices,
    }


def _safe_http_url(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned.startswith(("https://", "http://")):
            return cleaned
    return None


def _render_tool_event(event: dict[str, Any], index: int) -> None:
    tool_name = str(event.get("tool") or "unknown")
    args = event.get("args") or {}
    result = event.get("result")

    badge = "✅ OK"
    if event.get("error") or (isinstance(result, dict) and (result.get("error") or result.get("status") in {"error", "provider_error"})):
        badge = "❌ ERROR"
    elif isinstance(result, dict) and result.get("status") == "needs_confirmation":
        badge = "🛡️ Guardrail: Needs Confirmation"
    elif isinstance(result, dict) and result.get("awaiting_user"):
        badge = "⏸️ Waiting for User (clarify)"

    st.markdown(f"**{index}. `{tool_name}`** — {badge}")
    tab_summary, tab_args, tab_raw = st.tabs(["Kết quả tóm tắt", "Arguments", "Raw JSON"])

    with tab_args:
        st.json(args)

    with tab_raw:
        st.json(result if result is not None else event)

    with tab_summary:
        if event.get("error"):
            st.error(f"{event.get('error')}: {event.get('message') or ''}")
            return
        if not isinstance(result, dict):
            st.write(result)
            return
        if result.get("error"):
            st.error(f"{result.get('error')}: {result.get('message') or ''}")
            return
        if result.get("status") == "needs_confirmation":
            st.warning(str(result.get("message") or "Cần xác nhận từ người dùng."))
            return
        if result.get("awaiting_user"):
            st.info(
                f"Câu hỏi: {result.get('question') or ''}  \n"
                f"Kiểu phản hồi: `{result.get('response_type', 'text')}`"
                + (f" · Options: {result.get('options')}" if result.get("options") else "")
            )
            return
        if isinstance(result.get("markdown"), str) and result["markdown"].strip():
            st.markdown(result["markdown"])
            return

        items = result.get("items") or result.get("results") or []
        if isinstance(items, list) and items:
            st.caption(f"Trả về {len(items)} kết quả (hiển thị tối đa 5 mục đầu):")
            for item in items[:5]:
                if not isinstance(item, dict):
                    st.write(item)
                    continue
                title = str(item.get("title") or item.get("section") or "(Không tiêu đề)").strip()
                source = str(item.get("source") or item.get("policy_area") or "").strip()
                url = _safe_http_url(item.get("url") or item.get("pdf_url"))
                snippet = str(item.get("summary") or item.get("facts") or "").strip()
                if len(snippet) > 220:
                    snippet = snippet[:217] + "..."
                header = f"- **[{title}]({url})**" if url else f"- **{title}**"
                if source:
                    header += f" (`{source}`)"
                st.markdown(header)
                if snippet:
                    st.caption(snippet)
                if item.get("untrusted_text"):
                    st.warning("Đã cách ly dòng chỉ dẫn đáng ngờ vào `untrusted_text`.")
        else:
            st.json(result)


def init_session_state(default_provider: str) -> None:
    if "ui_turns" not in st.session_state:
        st.session_state.ui_turns = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None
    if "session_started_at" not in st.session_state:
        st.session_state.session_started_at = now_iso()
    if "session_stamp" not in st.session_state:
        st.session_state.session_stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = default_provider
    if "active_snapshot_key" not in st.session_state:
        st.session_state.active_snapshot_key = "current"


def reset_conversation() -> None:
    st.session_state.ui_turns = []
    st.session_state.chat_history = []
    st.session_state.pending_prompt = None
    st.session_state.session_started_at = now_iso()
    st.session_state.session_stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.pop("last_transcript_path", None)


def build_transcript_payload(
    *,
    version_label: str,
    provider_name: str,
    selected_model: str | None,
    artifacts: dict[str, Any],
    history_window: int,
    max_tool_rounds: int,
    turns: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    transcript_id = f"ui_{safe_slug(version_label)}_{safe_slug(provider_name)}_{st.session_state.session_stamp}"
    payload: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifacts["artifact_version"]),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(SYSTEM_PROMPT_PATH.relative_to(APP_ROOT)),
        "tools": str(TOOLS_YAML_PATH.relative_to(APP_ROOT)),
        "snapshot_commit": artifacts.get("snapshot_commit"),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": st.session_state.session_started_at,
        "updated_at": now_iso(),
        "turns": turns,
    }
    return transcript_id, payload


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])

    diag = extract_turn_diagnostics(turn)
    with st.chat_message("assistant"):
        if diag["provider_error"]:
            st.error(f"Lỗi Provider: `{diag['provider_error']}`")
        else:
            text = (turn.get("assistant_text") or "").strip()
            if text:
                st.markdown(text)
            else:
                st.info("(Agent không trả text bổ sung.)")

        if diag["tool_errors"]:
            error_lines = "\n".join(
                f"- `{err['tool']}` ({err['error']}): {err['message']}"
                for err in diag["tool_errors"]
            )
            st.error(f"Phát hiện lỗi từ tool (hiển thị trung thực theo yêu cầu):\n{error_lines}")

        if diag["needs_confirmation"]:
            for notice in diag["needs_confirmation"]:
                st.warning(f"🛡️ Bảo vệ hành động gửi: {notice}")

        if turn.get("status") == "max_tool_rounds":
            st.warning("Agent đã chạm giới hạn số vòng gọi tool (`max_tool_rounds`).")

        for notice in diag["untrusted_notices"]:
            st.warning(f"🔒 Trust boundary: {notice}")

        tool_events = turn.get("tool_events") or []
        rounds = turn.get("rounds") or []
        if tool_events or diag["provider_error"]:
            has_error = bool(diag["tool_errors"] or diag["provider_error"])
            status_label = "❌ Có lỗi" if has_error else (
                "⏸️ Chờ người dùng" if turn.get("status") == "waiting_for_user" else "✅ Hoàn tất"
            )
            st.caption(
                f"🔧 {len(tool_events)} tool call · {len(rounds)} round · Trạng thái: {status_label}"
            )
            if tool_events:
                with st.expander(
                    f"🔍 Chi tiết Tool Calls & Kết quả ({len(tool_events)})",
                    expanded=has_error,
                ):
                    for idx, event in enumerate(tool_events, start=1):
                        if idx > 1:
                            st.divider()
                        _render_tool_event(event, idx)


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .hero-box {
            padding: 0.9rem 1.15rem;
            border-radius: 0.75rem;
            border: 1px solid rgba(128, 128, 128, 0.25);
            background-color: rgba(128, 128, 128, 0.06);
            margin-bottom: 0.9rem;
        }
        .hero-title {
            font-size: 1.45rem;
            font-weight: 700;
            margin: 0 0 0.25rem 0;
        }
        .hero-sub {
            font-size: 0.95rem;
            opacity: 0.85;
            margin: 0;
        }
        .meta-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.6rem;
        }
        .meta-pill {
            font-size: 0.8rem;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            border: 1px solid rgba(128, 128, 128, 0.3);
            background-color: rgba(128, 128, 128, 0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def execute_turn(
    *,
    user_text: str,
    provider_name: str,
    model_override: str | None,
    version_label: str,
    artifacts: dict[str, Any],
    history_window: int,
    max_tool_rounds: int,
    save_transcript_enabled: bool,
) -> None:
    turn_index = len(st.session_state.ui_turns) + 1
    provider = make_provider(provider_name)
    resolved_model = model_override or getattr(provider, "default_model", None)

    messages = [
        {"role": "system", "content": artifacts["system_prompt"]},
        *trim_history(st.session_state.chat_history, history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=artifacts["openai_tools"],
            model=model_override,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        st.session_state.chat_history.append({"role": "user", "content": user_text})
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})
    except Exception as exc:
        turn_record.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {str(exc)}",
        })

    turn_record["ended_at"] = now_iso()
    st.session_state.ui_turns.append(turn_record)

    if save_transcript_enabled:
        transcript_id, payload = build_transcript_payload(
            version_label=version_label,
            provider_name=provider_name,
            selected_model=resolved_model,
            artifacts=artifacts,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
            turns=st.session_state.ui_turns,
        )
        transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
        write_transcript(transcript_path, payload)
        st.session_state.last_transcript_path = str(transcript_path.relative_to(APP_ROOT))


def main() -> None:
    st.set_page_config(
        page_title="Research Agent — NhomABCD",
        page_icon="🔎",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_runtime_env()
    init_session_state(detect_default_provider())
    inject_custom_css()

    with st.sidebar:
        st.header("⚙️ Cấu hình Agent")
        provider_options = list(PROVIDER_CONFIGS.keys())
        default_idx = provider_options.index(st.session_state.selected_provider)
        provider_name = st.selectbox(
            "Provider",
            options=provider_options,
            index=default_idx,
            format_func=lambda key: f"{PROVIDER_CONFIGS[key]['label']} ({key})",
        )
        st.session_state.selected_provider = provider_name

        provider_cfg = PROVIDER_CONFIGS[provider_name]
        env_var = provider_cfg["env"]
        if env_var:
            if os.getenv(env_var):
                st.caption(f"✅ Đã nạp `{env_var}`")
            else:
                st.warning(f"⚠️ Thiếu `{env_var}` trong `.env`")
        else:
            st.caption(f"🖥️ Local endpoint: `{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')}`")

        default_model_hint = str(provider_cfg["default_model"] or "")
        model_input = st.text_input(
            "Model (để trống = mặc định)",
            value="gemini-2.5-flash" if provider_name == "gemini" else "",
            placeholder=default_model_hint,
            key=f"model_override_{provider_name}",
        ).strip()
        model_override = model_input or None
        effective_model = model_override or default_model_hint

        snapshot_catalog = build_snapshot_catalog()
        snapshot_keys = list(snapshot_catalog.keys())
        if st.session_state.get("snapshot_selector") not in snapshot_catalog:
            st.session_state.snapshot_selector = "current"
        if st.session_state.active_snapshot_key not in snapshot_catalog:
            st.session_state.active_snapshot_key = "current"

        selected_snapshot_key = st.selectbox(
            "Phiên bản Agent (Prompt & Tools)",
            options=snapshot_keys,
            key="snapshot_selector",
            format_func=lambda key: snapshot_catalog[key]["label"],
        )
        if selected_snapshot_key != st.session_state.active_snapshot_key:
            reset_conversation()
            st.session_state.active_snapshot_key = selected_snapshot_key

        active_snapshot = snapshot_catalog[selected_snapshot_key]
        st.caption(f"ℹ️ {active_snapshot['note']}")
        if selected_snapshot_key == "current":
            default_ver = active_snapshot["version"]
            version_label = (
                st.text_input(
                    "Version label",
                    value=default_ver,
                    key=f"version_label_{default_ver}",
                ).strip()
                or default_ver
            )
        else:
            version_label = active_snapshot["version"]

        history_window = st.slider("History window (cặp lượt)", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Max tool rounds / lượt", min_value=1, max_value=8, value=4)
        save_transcript_enabled = st.checkbox("Tự động lưu transcript JSON", value=True)

        col_reset, col_reload = st.columns(2)
        with col_reset:
            if st.button("🗑️ Cuộc trò chuyện mới", width="stretch"):
                reset_conversation()
                st.rerun()
        with col_reload:
            if st.button("🔄 Nạp lại config", width="stretch"):
                discover_git_snapshots.clear()
                st.rerun()

        st.divider()
        st.subheader("⚡ Câu hỏi mẫu (Showdown)")
        for label, sample_text in SAMPLE_PROMPTS:
            if st.button(label, key=f"sample_{label}", width="stretch"):
                st.session_state.pending_prompt = sample_text
                st.rerun()

    try:
        artifacts = load_runtime_artifacts(version_label, active_snapshot)
    except Exception as exc:
        st.error(f"Không thể đọc artifacts (`system_prompt.md` / `tools.yaml`): {type(exc).__name__}: {exc}")
        st.stop()

    with st.sidebar:
        st.divider()
        st.subheader("🧰 Tools & Môi trường")
        with st.expander(f"Danh sách Tools ({len(artifacts['tool_declarations'])})", expanded=False):
            for decl in artifacts["tool_declarations"]:
                name = decl["name"]
                status_icon = "✅" if name in TOOL_FUNCTIONS else "❌ thiếu code"
                params = ", ".join((decl.get("parameters", {}).get("properties") or {}).keys())
                st.markdown(f"**`{name}`** ({status_icon})  \n{decl.get('description', '')}")
                if params:
                    st.caption(f"Params: `{params}`")

        with st.expander("System Prompt đang nạp", expanded=False):
            st.caption(f"Hash: `{artifacts['artifact_version'].prompt_hash[:12]}`")
            st.text(artifacts["system_prompt"])

        with st.expander("Trạng thái API Key Tools", expanded=False):
            for key_name, desc, required in TOOL_ENV_KEYS:
                ok = bool(os.getenv(key_name))
                icon = "✅" if ok else ("⚠️" if required else "➖")
                st.caption(f"{icon} `{key_name}` — {desc}")

        if st.session_state.ui_turns:
            transcript_id, payload = build_transcript_payload(
                version_label=version_label,
                provider_name=provider_name,
                selected_model=effective_model,
                artifacts=artifacts,
                history_window=history_window,
                max_tool_rounds=max_tool_rounds,
                turns=st.session_state.ui_turns,
            )
            st.divider()
            st.subheader("📝 Transcript phiên hiện tại")
            if st.session_state.get("last_transcript_path"):
                st.caption(f"Đã lưu: `{st.session_state.last_transcript_path}`")
            st.download_button(
                "⬇️ Tải Transcript JSON",
                data=json.dumps(payload, ensure_ascii=False, indent=2, default=str),
                file_name=f"{transcript_id}.transcript.json",
                mime="application/json",
                width="stretch",
            )

    art_ver = html.escape(artifacts["artifact_version"].artifact_version)
    safe_provider = html.escape(provider_name)
    safe_model = html.escape(effective_model)
    commit_pill = (
        f'<span class="meta-pill">Git snapshot: <b>{html.escape(active_snapshot["short_commit"])}</b></span>'
        if active_snapshot.get("short_commit")
        else '<span class="meta-pill">Nguồn: <b>Trên đĩa</b></span>'
    )
    st.markdown(
        f"""
        <div class="hero-box">
            <div class="hero-title">🔎 Research Agent — Team NhomABCD</div>
            <p class="hero-sub">
                Tìm tin web theo chủ đề/thời gian, theo dõi X/Twitter, đọc URL, tra arXiv, kiểm tra DOI Crossref &amp; policy nội bộ,
                hỏi lại khi thiếu thông tin và xác nhận trước khi gửi Telegram.
            </p>
            <div class="meta-strip">
                <span class="meta-pill">Version: <b>{art_ver}</b></span>
                {commit_pill}
                <span class="meta-pill">Provider: <b>{safe_provider}</b> / <b>{safe_model}</b></span>
                <span class="meta-pill">Tools: <b>{len(artifacts['tool_declarations'])}</b></span>
                <span class="meta-pill">Transcript: <b>{'Bật' if save_transcript_enabled else 'Tắt'}</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if artifacts["missing_impls"]:
        st.warning(
            f"Contract warning: Các tool khai báo trong `tools.yaml` chưa có trong `TOOL_FUNCTIONS`: "
            f"`{', '.join(artifacts['missing_impls'])}`"
        )

    if not st.session_state.ui_turns and not st.session_state.pending_prompt:
        st.info(
            "👋 Chào bạn! Hãy nhập câu hỏi bên dưới hoặc chọn một **Câu hỏi mẫu** ở thanh bên trái để thử các khả năng của Research Agent "
            "(tìm tin, hỏi lại khi thiếu thông tin, xác nhận trước khi gửi, và hiển thị minh bạch toàn bộ tool call/lỗi)."
        )

    for turn in st.session_state.ui_turns:
        render_turn(turn)

    if st.session_state.ui_turns and st.session_state.ui_turns[-1].get("status") == "waiting_for_user":
        last_diag = extract_turn_diagnostics(st.session_state.ui_turns[-1])
        clarify = last_diag["clarify_info"] or {"response_type": "text", "options": []}
        response_type = clarify.get("response_type", "text")
        options = clarify.get("options") or []

        if response_type == "yes_no":
            st.info("🛡️ Agent đang chờ bạn xác nhận trước khi thực hiện hành động:")
            col_yes, col_no, _ = st.columns([1, 1, 2])
            with col_yes:
                if st.button("✅ Có, xác nhận gửi", key="clarify_yes", width="stretch"):
                    st.session_state.pending_prompt = "Đồng ý, bạn gửi đi nhé."
                    st.rerun()
            with col_no:
                if st.button("❌ Không, hủy bỏ", key="clarify_no", width="stretch"):
                    st.session_state.pending_prompt = "Không, hủy giúp mình nhé."
                    st.rerun()
        elif response_type == "choice" and options:
            st.info("👇 Chọn nhanh một phương án hoặc nhập trực tiếp bên dưới:")
            cols = st.columns(min(len(options), 4))
            for idx, opt in enumerate(options):
                with cols[idx % len(cols)]:
                    if st.button(str(opt), key=f"clarify_opt_{idx}", width="stretch"):
                        st.session_state.pending_prompt = str(opt)
                        st.rerun()
        else:
            st.info("💬 Agent đang chờ bạn bổ sung thông tin ở ô nhập bên dưới (ví dụ: tên tài khoản X hoặc link bài viết).")

    user_input = st.chat_input("Nhập yêu cầu cho Research Agent... (ví dụ: Tin AI hôm nay có gì?)")
    if user_input and user_input.strip():
        st.session_state.pending_prompt = user_input.strip()

    if st.session_state.pending_prompt:
        prompt_text = str(st.session_state.pop("pending_prompt")).strip()
        if prompt_text:
            with st.chat_message("user"):
                st.markdown(prompt_text)
            with st.chat_message("assistant"):
                with st.spinner("Agent đang suy nghĩ và gọi tool..."):
                    execute_turn(
                        user_text=prompt_text,
                        provider_name=provider_name,
                        model_override=model_override,
                        version_label=version_label,
                        artifacts=artifacts,
                        history_window=history_window,
                        max_tool_rounds=max_tool_rounds,
                        save_transcript_enabled=save_transcript_enabled,
                    )
            st.rerun()


if __name__ == "__main__":
    main()
