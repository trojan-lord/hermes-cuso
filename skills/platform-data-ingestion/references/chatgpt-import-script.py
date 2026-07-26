#!/usr/bin/env python3
"""Import ChatGPT data export into Hermes state.db sessions.

Usage:
  1. User provides ChatGPT ZIP (Google Drive link, upload, or local path)
  2. Download and unzip
  3. Run this script: python3 chatgpt-import-script.py [path-to-unzipped-dir]

Requires: sqlite3 (stdlib), no external deps.
Expects Hermes state.db at ~/.hermes/state.db.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DB = os.path.expanduser("~/.hermes/state.db")
SOURCE = "chatgpt_import"


def flatten_conversation(conv: dict) -> list[dict]:
    """Convert ChatGPT's tree mapping to a linear message list.

    ChatGPT's export uses parent pointers (no children arrays).
    Walk backwards from current_node, then reverse for chronological order.
    """
    mapping = conv.get("mapping", {})
    if not mapping:
        return []

    current_node = conv.get("current_node")
    if not current_node:
        # Fallback: find node with no parent (root)
        for nid, node in mapping.items():
            if node.get("parent") is None:
                current_node = nid
                break
    if not current_node:
        return []

    messages = []
    node_id = current_node
    while node_id:
        node = mapping.get(node_id, {})
        msg = node.get("message")
        parent = node.get("parent")

        if msg:
            role = msg.get("author", {}).get("role", "")
            if role in ("user", "assistant"):
                content_parts = msg.get("content", {}).get("parts", [])
                text_parts = [p for p in content_parts if p and str(p).strip()]
                content = "\n".join(str(p) for p in text_parts) if text_parts else None
                if content:
                    timestamp = msg.get("create_time") or msg.get("update_time") or conv.get("create_time", 0)
                    messages.append({
                        "role": role,
                        "content": content,
                        "timestamp": timestamp,
                    })

        node_id = parent

    # Reverse to get chronological order
    messages.reverse()
    return messages


def generate_session_id(timestamp: float) -> str:
    """Generate a Hermes-style session ID from a timestamp."""
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    random_part = os.urandom(3).hex()
    return f"{dt.strftime('%Y%m%d_%H%M%S')}_{random_part}"


def import_conversations(db_path: str, export_dir: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get current max message ID
    cur.execute("SELECT MAX(id) FROM messages")
    max_msg_id = cur.fetchone()[0] or 0

    total_sessions = 0
    total_messages = 0
    skipped_empty = 0
    skipped_short = 0

    # Process all conversation files
    conv_files = sorted(export_dir.glob("conversations-*.json"))
    for conv_file in conv_files:
        with open(conv_file) as f:
            conversations = json.load(f)

        for conv in conversations:
            title = conv.get("title", "Untitled")
            create_time = conv.get("create_time", 0)
            update_time = conv.get("update_time", 0)

            messages = flatten_conversation(conv)
            if not messages:
                skipped_empty += 1
                continue

            # Skip single-message conversations (probably empty or accidental)
            if len(messages) < 2:
                skipped_short += 1
                continue

            session_id = generate_session_id(create_time or update_time or 0)

            # Make title unique by appending suffix if needed
            base_title = title
            suffix = 2
            while True:
                try:
                    cur.execute(
                        """INSERT INTO sessions
                           (id, source, started_at, ended_at, message_count, title, archived)
                           VALUES (?, ?, ?, ?, ?, ?, 0)""",
                        (session_id, SOURCE, create_time, update_time, len(messages), title),
                    )
                    break
                except sqlite3.IntegrityError:
                    title = f"{base_title} ({suffix})"
                    suffix += 1

            # Insert messages
            for msg in messages:
                max_msg_id += 1
                cur.execute(
                    """INSERT INTO messages
                       (id, session_id, role, content, timestamp, active, compacted)
                       VALUES (?, ?, ?, ?, ?, 1, 0)""",
                    (max_msg_id, session_id, msg["role"], msg["content"], msg["timestamp"]),
                )
                total_messages += 1

            total_sessions += 1

    conn.commit()

    # Rebuild FTS index
    print("Rebuilding FTS index...")
    cur.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
    conn.commit()

    conn.close()
    return total_sessions, total_messages, skipped_empty, skipped_short


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path-to-unzipped-chatgpt-export>")
        print(f"  Expected to find conversations-*.json in the directory")
        sys.exit(1)

    export_dir = Path(sys.argv[1])
    if not export_dir.exists():
        print(f"Directory not found: {export_dir}")
        sys.exit(1)

    print(f"Importing ChatGPT conversations into {STATE_DB}")
    print(f"Source: {export_dir}")

    sessions, messages, empty, short = import_conversations(STATE_DB, export_dir)

    print(f"\nDone!")
    print(f"  Sessions imported: {sessions}")
    print(f"  Messages imported: {messages}")
    print(f"  Skipped (empty): {empty}")
    print(f"  Skipped (single msg): {short}")
