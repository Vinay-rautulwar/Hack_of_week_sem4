

import re
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# 1.  KNOWN INTENTS + KEYWORDS
# ---------------------------------------------------------------------------
INTENT_KEYWORDS: dict[str, list[str]] = {
    "exam":       ["exam","test","examination","timetable","schedule","date","paper"],
    "fees":       ["fees","fee","tuition","payment","cost","price","charges"],
    "admission":  ["admission","apply","enroll","registration","joining","eligibility"],
    "hostel":     ["hostel","accommodation","dorm","dormitory","stay","room","lodge"],
    "placement":  ["placement","job","career","recruit","internship","hire","company"],
    "faculty":    ["faculty","teacher","professor","staff","lecturer"],
    "library":    ["library","book","journal","reading","resource"],
    "transport":  ["transport","bus","shuttle","travel","commute","route"],
    "scholarship":["scholarship","financial aid","waiver","merit","stipend","grant"],
    "courses":    ["course","program","degree","branch","subject","discipline"],
}

# Responses for known intents
INTENT_RESPONSES: dict[str, str] = {
    "exam":       "Exams are conducted per the academic calendar. Ask 'When is SEM 5 CS exam?' for specifics.",
    "fees":       "Fees vary by course. Visit our website or contact the accounts office at fees@institute.edu.",
    "admission":  "Admissions are open. Apply at admissions.institute.edu or call +91-98765-43210.",
    "hostel":     "Hostel is available for boys and girls. Contact hostel@institute.edu for bookings.",
    "placement":  "Our placement cell supports internships and jobs. Email placement@institute.edu.",
    "faculty":    "Faculty info is available on our website under the Departments section.",
    "library":    "Library is open 8 AM – 8 PM on weekdays. Contact library@institute.edu.",
    "transport":  "Bus routes from major city points. Contact transport@institute.edu for details.",
    "scholarship":"Scholarships based on merit/category. Apply via scholarship.institute.edu.",
    "courses":    "We offer UG and PG programs. Visit courses.institute.edu for the full list.",
}

ADVISOR_MSG = (
    "It seems your question is outside my scope. You can:\n"
    "  • Email our help desk: helpdesk@institute.edu\n"
    "  • Call: +91-98765-43210 (Mon–Fri, 9 AM – 5 PM)\n"
    "  • Visit: https://institute.edu/contact\n"
    "A human advisor will be happy to assist you!"
)

SUGGESTION_TOPICS = list(INTENT_KEYWORDS.keys())

# ---------------------------------------------------------------------------
# 2.  SCORING + CLASSIFICATION
# ---------------------------------------------------------------------------
def score_intents(text: str) -> dict[str, float]:
    """Return a confidence score (0–1) for each intent."""
    tl = text.lower()
    scores: dict[str, float] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in tl)
        # Fuzzy bonus: partial word matches
        fuzzy = sum(
            SequenceMatcher(None, kw, word).ratio()
            for kw in keywords
            for word in tl.split()
            if SequenceMatcher(None, kw, word).ratio() > 0.75
        )
        scores[intent] = hits + 0.3 * fuzzy
    return scores


def classify(text: str) -> tuple[str | None, float]:
    """
    Returns (top_intent, confidence).
    confidence is normalised to 0–1 range relative to max possible.
    """
    scores = score_intents(text)
    if not scores:
        return None, 0.0
    best_intent = max(scores, key=scores.get)  # type: ignore[arg-type]
    best_score  = scores[best_intent]
    return (best_intent, min(best_score / 3.0, 1.0)) if best_score > 0 else (None, 0.0)


# ---------------------------------------------------------------------------
# 3.  CLARIFICATION STRATEGY
# ---------------------------------------------------------------------------
def ask_clarification(partial_intent: str | None, scores: dict[str, float]) -> str:
    """Build a targeted clarification question."""
    if partial_intent:
        return (
            f"I think you're asking about **{partial_intent}**, but I'm not sure. "
            f"Could you give more details? For example:\n"
            + _example_for(partial_intent)
        )
    # Show top 3 guesses
    top = sorted(scores, key=scores.get, reverse=True)[:3]  # type: ignore[arg-type]
    topic_list = ", ".join(top) if top else "exams, fees, or admissions"
    return (
        f"I'm not sure what you're asking about. Are you asking about: {topic_list}?\n"
        f"Try rephrasing, or type one of these topics directly."
    )


def suggest_topics() -> str:
    topics = ", ".join(SUGGESTION_TOPICS[:6])
    return (
        f"I can help with: {topics}, and more.\n"
        f"Type a topic or ask a specific question like 'When is SEM 5 CS exam?'"
    )


def _example_for(intent: str) -> str:
    examples = {
        "exam":       "  'When is the SEM 5 CS exam?'",
        "fees":       "  'What are the CS course fees?'",
        "admission":  "  'How do I apply for admission?'",
        "hostel":     "  'Is hostel available for girls?'",
        "placement":  "  'What companies visit for placement?'",
        "faculty":    "  'Who teaches Computer Science?'",
        "library":    "  'What are the library hours?'",
        "transport":  "  'Is there a bus from city centre?'",
        "scholarship":"  'Am I eligible for a scholarship?'",
        "courses":    "  'What UG courses are available?'",
    }
    return examples.get(intent, "  Please provide more details.")


# ---------------------------------------------------------------------------
# 4.  MAIN HANDLER  (tracks failure streak for escalation)
# ---------------------------------------------------------------------------
class OutOfScopeHandler:
    CONFIDENCE_THRESHOLD = 0.25  # below this → clarify or suggest
    ESCALATION_THRESHOLD = 2     # fail count before routing to human

    def __init__(self):
        self.fail_streak = 0

    def respond(self, user_input: str) -> str:
        if not user_input.strip():
            return "Please type your question."

        intent, confidence = classify(user_input)
        scores = score_intents(user_input)

        print(f"  [intent={intent}, confidence={confidence:.2f}, fail_streak={self.fail_streak}]")

        # ── High confidence: answer directly ──────────────────────────────
        if confidence >= self.CONFIDENCE_THRESHOLD and intent:
            self.fail_streak = 0
            return INTENT_RESPONSES[intent]

        # ── Immediately escalate if user has failed repeatedly ─────────────
        if self.fail_streak >= self.ESCALATION_THRESHOLD:
            self.fail_streak = 0
            return ADVISOR_MSG

        self.fail_streak += 1

        # ── Low confidence but some signal: ask targeted clarification ─────
        if 0 < confidence < self.CONFIDENCE_THRESHOLD:
            return ask_clarification(intent, scores)

        # ── Zero signal: suggest topics ────────────────────────────────────
        top_score = max(scores.values()) if scores else 0
        if top_score == 0:
            if self.fail_streak >= self.ESCALATION_THRESHOLD - 1:
                return ADVISOR_MSG
            return suggest_topics()

        return ask_clarification(None, scores)


# ---------------------------------------------------------------------------
# 5.  COMMAND-LINE DEMO
# ---------------------------------------------------------------------------
def main() -> None:
    handler = OutOfScopeHandler()
    print("=" * 60)
    print("   Out-of-Scope Handler  (type 'quit' to exit)")
    print("=" * 60)
    print("\nTest with unclear questions like:")
    print("  • 'huh?'")
    print("  • 'What about the thing tomorrow?'")
    print("  • 'pizza?'   (3 times to trigger escalation)")
    print("  • 'exam date' (partial — asks clarification)")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break
        print(f"Bot: {handler.respond(user_input)}")


if __name__ == "__main__":
    main()
