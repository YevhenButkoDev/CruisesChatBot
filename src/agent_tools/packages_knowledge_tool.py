from __future__ import annotations

from pathlib import Path
import re
from typing import Optional

# src/agent_tools -> src
BASE_DIR = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = BASE_DIR / "knowledge" / "packages"

LINE_TO_FILE = {
    "royal caribbean": "royal_caribbean.md",
    "rci": "royal_caribbean.md",
    "celebrity": "celebrity.md",
    "ncl": "ncl.md",
    "norwegian": "ncl.md",
    "norwegian cruise line": "ncl.md",
}

# intent keywords
TOPIC_KEYWORDS = {
    "included": ["included", "what is included", "included in", "base fare", "fare includes"],
    "drinks": ["drink", "drinks", "beverage", "alcohol", "cocktail", "beer", "wine", "soft drink", "package"],
    "wifi": ["wifi", "wi-fi", "internet", "streaming", "voom"],
    "gratuities": ["gratuity", "gratuities", "tips", "service charge", "service charges"],
    "dining": ["dining", "restaurants", "specialty dining", "speciality dining"],
}

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def _detect_line(user_text: str, cruise_line: Optional[str]) -> Optional[str]:
    if cruise_line:
        cl = _normalize(cruise_line)
        for k in LINE_TO_FILE:
            if k in cl:
                return k
    t = _normalize(user_text)
    for k in LINE_TO_FILE:
        if k in t:
            return k
    return None

def _detect_topic(user_text: str) -> Optional[str]:
    t = _normalize(user_text)
    for topic, keys in TOPIC_KEYWORDS.items():
        if any(k in t for k in keys):
            return topic
    return None

def _extract_sections(md: str) -> list[tuple[str, str]]:
    """
    Split markdown into sections by headings.
    Returns list of (heading, content) where heading includes the heading line.
    """
    if not md:
        return []
    parts = re.split(r"\n(?=##\s)", md)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        heading = p.splitlines()[0].strip()
        out.append((heading, p))
    return out

def get_packages_knowledge(query: str, cruise_line: Optional[str] = None) -> str:
    """
    Returns relevant knowledge snippet about packages/inclusions.
    - Does not mention files/tools.
    - Returns short, relevant text (not full doc).
    """
    q = query or ""
    line_key = _detect_line(q, cruise_line)
    if not line_key:
        return (
            "To answer accurately, please confirm the cruise line: Royal Caribbean, Celebrity, or NCL."
        )

    file_name = LINE_TO_FILE[line_key]
    file_path = KNOWLEDGE_DIR / file_name
    if not file_path.exists():
        return "Package information is currently unavailable for this cruise line."

    md = file_path.read_text(encoding="utf-8")
    topic = _detect_topic(q)

    # If no topic detected, return a compact “menu” of what can be answered
    if not topic:
        return (
            "I can help with what’s included in the base fare, drink packages, Wi-Fi/internet, and gratuities. "
            "What exactly would you like to know?"
        )

    sections = _extract_sections(md)

    # Score sections by keyword overlap
    keys = TOPIC_KEYWORDS.get(topic, [])
    scored: list[tuple[int, str]] = []
    for _, content in sections:
        c_low = content.lower()
        score = sum(1 for k in keys if k in c_low)
        if score > 0:
            scored.append((score, content))

    if not scored:
        # fallback: return top of doc (usually has “included/not included”)
        head = "\n".join(md.splitlines()[:80]).strip()
        return head if head else "No relevant package information found."

    scored.sort(key=lambda x: x[0], reverse=True)

    # Return up to 2 best sections, capped
    snippet = "\n\n".join(s for _, s in scored[:2]).strip()
    lines = snippet.splitlines()
    return "\n".join(lines[:140]).strip()
