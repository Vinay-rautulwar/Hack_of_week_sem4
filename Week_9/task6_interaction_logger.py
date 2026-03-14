

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

LOG_FILE = Path("chatbot_interactions.jsonl")

# ---------------------------------------------------------------------------
# 1.  LOGGER
# ---------------------------------------------------------------------------
class InteractionLogger:
    def __init__(self, log_path: Path = LOG_FILE):
        self.log_path = log_path

    def log(
        self,
        session_id: str,
        turn: int,
        user_input: str,
        bot_response: str,
        intent: str | None = None,
        confidence: float | None = None,
        entities: dict | None = None,
        resolved: bool = True,
    ) -> None:
        record = {
            "timestamp":   datetime.utcnow().isoformat() + "Z",
            "session_id":  session_id,
            "turn":        turn,
            "user_input":  user_input,
            "bot_response":bot_response,
            "intent":      intent,
            "confidence":  confidence,
            "entities":    entities or {},
            "resolved":    resolved,
            "label":       None,   # filled in during labelling
            "notes":       "",
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def load(self) -> list[dict]:
        if not self.log_path.exists():
            return []
        records = []
        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return records


# ---------------------------------------------------------------------------
# 2.  AUTO-LABELLER
#     Labels each record heuristically so we have a labelled sample
#     without requiring manual annotation.
# ---------------------------------------------------------------------------
LABEL_RULES: list[tuple[str, callable]] = [
    ("unresolved_ooscope",  lambda r: not r["resolved"] and r["confidence"] is not None and r["confidence"] < 0.25),
    ("low_confidence",      lambda r: r["confidence"] is not None and 0.0 < r["confidence"] < 0.25),
    ("no_entities",         lambda r: r["resolved"] and not r["entities"]),
    ("escalated_to_human",  lambda r: "helpdesk@institute.edu" in r["bot_response"]),
    ("successful",          lambda r: r["resolved"] and r["confidence"] is not None and r["confidence"] >= 0.25),
    ("greeting",            lambda r: r["intent"] == "greeting"),
]

def auto_label(record: dict) -> str:
    for label, condition in LABEL_RULES:
        try:
            if condition(record):
                return label
        except Exception:
            pass
    return "other"


# ---------------------------------------------------------------------------
# 3.  ANALYSIS + IMPROVEMENT PROPOSALS
# ---------------------------------------------------------------------------
def analyse(records: list[dict]) -> str:
    if not records:
        return "No interactions logged yet."

    total   = len(records)
    labelled = [r | {"label": r["label"] or auto_label(r)} for r in records]

    # --- Basic stats ---
    resolved_count   = sum(1 for r in labelled if r["resolved"])
    unresolved_count = total - resolved_count
    label_counts     = Counter(r["label"] for r in labelled)

    # --- Intent distribution ---
    intent_counts = Counter(r["intent"] for r in labelled if r["intent"])
    unknown_count = sum(1 for r in labelled if not r["intent"])

    # --- Unresolved queries (potential new FAQs) ---
    unresolved_queries = [
        r["user_input"] for r in labelled
        if not r["resolved"] or r["label"] in ("unresolved_ooscope", "low_confidence")
    ]

    # --- Repeated unanswered patterns ---
    word_freq: Counter = Counter()
    for q in unresolved_queries:
        tokens = re.sub(r"[^\w\s]","",q.lower()).split()
        word_freq.update(tokens)
    stop = {"i","the","a","an","is","are","was","were","what","when","where","how","for","of","to","do","can","please","my"}
    top_words = [(w, c) for w, c in word_freq.most_common(15) if w not in stop and len(w) > 2]

    lines = [
        "=" * 60,
        "  CHATBOT INTERACTION ANALYSIS REPORT",
        f"  Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
        "=" * 60,
        "",
        "── OVERVIEW ──────────────────────────────────────────────",
        f"  Total interactions  : {total}",
        f"  Resolved            : {resolved_count} ({100*resolved_count//total}%)",
        f"  Unresolved          : {unresolved_count} ({100*unresolved_count//total}%)",
        "",
        "── LABEL DISTRIBUTION ────────────────────────────────────",
    ]
    for label, count in label_counts.most_common():
        bar = "█" * (count * 20 // max(label_counts.values(), default=1))
        lines.append(f"  {label:<25} {count:>4}  {bar}")

    lines += [
        "",
        "── INTENT DISTRIBUTION ───────────────────────────────────",
    ]
    for intent, count in intent_counts.most_common():
        lines.append(f"  {intent:<20} {count:>4}")
    if unknown_count:
        lines.append(f"  {'(unclassified)':<20} {unknown_count:>4}")

    lines += [
        "",
        "── TOP WORDS IN UNRESOLVED QUERIES ───────────────────────",
    ]
    if top_words:
        for word, freq in top_words[:10]:
            lines.append(f"  '{word}'  — appeared {freq}×")
    else:
        lines.append("  (none — all queries resolved)")

    # --- Proposed improvements ---
    lines += [
        "",
        "── PROPOSED IMPROVEMENTS ─────────────────────────────────",
    ]

    suggestions: list[str] = []

    # New intents from unknown queries
    if unknown_count > 0:
        suggestions.append(
            f"[New Intent] {unknown_count} queries were unclassified. "
            "Review these and add new intent-keyword groups."
        )

    # New FAQs from repeated unresolved patterns
    high_freq_words = [w for w, c in top_words if c >= 2]
    if high_freq_words:
        suggestions.append(
            f"[New FAQ] Terms '{', '.join(high_freq_words[:5])}' appear often in "
            "unresolved queries. Add FAQ entries for these topics."
        )

    # Escalation rate
    escalated = label_counts.get("escalated_to_human", 0)
    if escalated / total > 0.15:
        suggestions.append(
            f"[Pattern Fix] {escalated} interactions ({100*escalated//total}%) "
            "were escalated to human advisors — above 15% threshold. "
            "Review these conversations and add more response patterns."
        )

    # Low confidence rate
    low_conf = label_counts.get("low_confidence", 0)
    if low_conf / total > 0.10:
        suggestions.append(
            f"[Synonym Expansion] {low_conf} queries had low confidence. "
            "Add more synonyms or rephrasings to the keyword dictionary."
        )

    if not suggestions:
        suggestions.append("All metrics look healthy! Keep logging to detect future drift.")

    for s in suggestions:
        lines.append(f"  • {s}")

    # Sample unresolved queries
    if unresolved_queries:
        lines += ["", "── SAMPLE UNRESOLVED QUERIES (for manual review) ─────────"]
        for q in unresolved_queries[:8]:
            lines.append(f"  ? {q}")

    lines += ["", "=" * 60]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4.  DEMO CHATBOT (wraps a simple FAQ bot + logs everything)
# ---------------------------------------------------------------------------
FAQ_RESPONSES: dict[str, str] = {
    "exam":      "Exams follow the academic calendar. Ask 'SEM 5 CS exam date' for specifics.",
    "fees":      "Fees vary by course. Contact fees@institute.edu.",
    "hostel":    "Hostel available for boys & girls. Email hostel@institute.edu.",
    "placement": "Placement cell supports internships and jobs. See placement.institute.edu.",
    "courses":   "We offer UG & PG programs. Visit courses.institute.edu.",
}
INTENT_KW: dict[str, list[str]] = {
    "exam":["exam","test","timetable","schedule"],
    "fees":["fee","fees","tuition","cost","payment"],
    "hostel":["hostel","accommodation","dorm","stay"],
    "placement":["placement","job","career","recruit"],
    "courses":["course","program","degree","branch"],
}

def simple_classify(text: str) -> tuple[str | None, float]:
    tl = text.lower()
    for intent, kws in INTENT_KW.items():
        hits = sum(1 for kw in kws if kw in tl)
        if hits:
            return intent, min(hits / 2.0, 1.0)
    return None, 0.0

def demo_chat(session_id: str, user_input: str, turn: int, logger: InteractionLogger) -> str:
    intent, conf = simple_classify(user_input)
    if intent:
        response = FAQ_RESPONSES[intent]
        resolved = True
    else:
        response = "I'm not sure about that. Please contact helpdesk@institute.edu."
        resolved = False

    logger.log(
        session_id  = session_id,
        turn        = turn,
        user_input  = user_input,
        bot_response= response,
        intent      = intent,
        confidence  = conf if intent else 0.0,
        resolved    = resolved,
    )
    return response


# ---------------------------------------------------------------------------
# 5.  ENTRY POINT
# ---------------------------------------------------------------------------
def main() -> None:
    logger = InteractionLogger()

    if "--analyse" in sys.argv:
        records = logger.load()
        print(analyse(records))
        return

    import uuid
    session_id = str(uuid.uuid4())[:8]
    turn = 0

    print("=" * 60)
    print("   Logged FAQ Chatbot  (type 'analyse' to see report, 'quit' to exit)")
    print(f"   Session: {session_id}  |  Log file: {LOG_FILE}")
    print("=" * 60)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit","exit"}:
            print("Bot: Goodbye! All interactions have been logged.")
            break
        if user_input.lower() == "analyse":
            records = logger.load()
            print(analyse(records))
            continue
        turn += 1
        response = demo_chat(session_id, user_input, turn, logger)
        print(f"Bot: {response}")
        print(f"     [logged turn {turn} to {LOG_FILE}]")


if __name__ == "__main__":
    main()
