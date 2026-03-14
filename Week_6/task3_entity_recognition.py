
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# 1.  EXAM DATABASE
#     Keys are (semester, course_code). Values are exam detail dicts.
# ---------------------------------------------------------------------------
EXAM_DB: dict[tuple[str, str], dict] = {
    ("1", "CS"):   {"date": "2025-05-10", "time": "10:00 AM", "room": "Hall A"},
    ("2", "CS"):   {"date": "2025-05-12", "time": "10:00 AM", "room": "Hall A"},
    ("3", "CS"):   {"date": "2025-05-14", "time": "02:00 PM", "room": "Lab 3"},
    ("4", "CS"):   {"date": "2025-05-16", "time": "10:00 AM", "room": "Hall B"},
    ("5", "CS"):   {"date": "2025-05-18", "time": "10:00 AM", "room": "Hall C"},
    ("6", "CS"):   {"date": "2025-05-20", "time": "02:00 PM", "room": "Hall C"},
    ("1", "MATH"): {"date": "2025-05-11", "time": "09:00 AM", "room": "Hall A"},
    ("2", "MATH"): {"date": "2025-05-13", "time": "09:00 AM", "room": "Hall A"},
    ("3", "MATH"): {"date": "2025-05-15", "time": "09:00 AM", "room": "Hall B"},
    ("4", "MATH"): {"date": "2025-05-17", "time": "09:00 AM", "room": "Hall B"},
    ("5", "MATH"): {"date": "2025-05-19", "time": "09:00 AM", "room": "Hall C"},
    ("1", "PHY"):  {"date": "2025-05-12", "time": "11:00 AM", "room": "Hall A"},
    ("2", "PHY"):  {"date": "2025-05-14", "time": "11:00 AM", "room": "Hall A"},
    ("3", "PHY"):  {"date": "2025-05-16", "time": "11:00 AM", "room": "Lab 1"},
    ("1", "ENG"):  {"date": "2025-05-13", "time": "03:00 PM", "room": "Hall B"},
    ("2", "ENG"):  {"date": "2025-05-15", "time": "03:00 PM", "room": "Hall B"},
    ("1", "CHEM"): {"date": "2025-05-14", "time": "10:00 AM", "room": "Lab 2"},
    ("2", "CHEM"): {"date": "2025-05-16", "time": "10:00 AM", "room": "Lab 2"},
}

# Map common aliases to canonical course codes
COURSE_ALIASES: dict[str, str] = {
    "cs": "CS", "computer science": "CS", "comp sci": "CS", "programming": "CS",
    "math": "MATH", "maths": "MATH", "mathematics": "MATH",
    "phy": "PHY", "physics": "PHY",
    "eng": "ENG", "english": "ENG",
    "chem": "CHEM", "chemistry": "CHEM",
}

# ---------------------------------------------------------------------------
# 2.  ENTITY EXTRACTION
# ---------------------------------------------------------------------------
def extract_entities(text: str) -> dict:
    """
    Extract semester number, course code, and optional date from raw text.
    Returns a dict with keys: 'semester', 'course', 'date'
    (values are None if not found).
    """
    text_lower = text.lower()
    entities: dict = {"semester": None, "course": None, "date": None}

    # --- Semester: "sem 5", "semester 3", "3rd semester", "third year" etc. ---
    sem_patterns = [
        r"\bsem(?:ester)?\s*(\d)\b",          # sem 5 / semester 5
        r"\b(\d)(?:st|nd|rd|th)?\s*sem(?:ester)?\b",  # 5th sem
        r"\b(first|second|third|fourth|fifth|sixth)\s*(?:year|sem(?:ester)?)\b",
    ]
    WORD_TO_NUM = {
        "first": "1", "second": "2", "third": "3",
        "fourth": "4", "fifth": "5", "sixth": "6",
    }
    for pat in sem_patterns:
        m = re.search(pat, text_lower)
        if m:
            val = m.group(1)
            entities["semester"] = WORD_TO_NUM.get(val, val)
            break

    # --- Course code: try aliases first, then bare uppercase tokens ---
    for alias, code in COURSE_ALIASES.items():
        if alias in text_lower:
            entities["course"] = code
            break
    if not entities["course"]:
        # Fall back: look for 2-5 uppercase letters in original text
        m = re.search(r"\b([A-Z]{2,5})\b", text)
        if m:
            candidate = m.group(1)
            if candidate not in {"SEM", "FOR", "THE", "AND", "WHEN", "IS"}:
                entities["course"] = candidate

    # --- Date: "on 15 May" / "May 15" / "15/05/2025" etc. ---
    date_pat = r"\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b|\b(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)\b"
    dm = re.search(date_pat, text_lower)
    if dm:
        entities["date"] = dm.group(0)

    return entities


# ---------------------------------------------------------------------------
# 3.  RESPONSE GENERATOR
# ---------------------------------------------------------------------------
def generate_response(question: str) -> str:
    entities = extract_entities(question)
    sem   = entities["semester"]
    course = entities["course"]

    print(f"  [Entities detected → semester={sem}, course={course}, date={entities['date']}]")

    if sem and course:
        key = (sem, course)
        if key in EXAM_DB:
            info = EXAM_DB[key]
            return (
                f"The SEM {sem} {course} exam is scheduled on {info['date']} "
                f"at {info['time']} in {info['room']}."
            )
        else:
            return (
                f"Sorry, I couldn't find exam details for SEM {sem} {course}. "
                f"Please check the official notice board or contact the exam cell."
            )

    if sem and not course:
        # List all courses for that semester
        available = [c for (s, c) in EXAM_DB if s == sem]
        if available:
            return (
                f"For SEM {sem}, I have exam info for: {', '.join(sorted(set(available)))}. "
                f"Which course are you asking about?"
            )
        return f"No exam data found for SEM {sem}. Please verify with the exam cell."

    if course and not sem:
        available = [s for (s, c) in EXAM_DB if c == course]
        if available:
            return (
                f"I have {course} exam info for semesters: {', '.join(sorted(set(available)))}. "
                f"Which semester are you asking about?"
            )
        return f"No exam data found for {course}. Please verify with the exam cell."

    return (
        "I couldn't detect a semester or course in your question. "
        "Try asking something like: 'When is SEM 5 CS exam?' "
        "or 'Show me the SEM 3 MATH schedule'."
    )


# ---------------------------------------------------------------------------
# 4.  COMMAND-LINE DEMO
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("   Entity Recognition Chatbot  (type 'quit' to exit)")
    print("=" * 60)
    sample_queries = [
        "When is SEM 5 CS exam?",
        "What date is the third semester math test?",
        "Show timetable for sem 2 physics",
        "Is there an exam tomorrow?",
    ]
    print("\nSample queries to try:")
    for q in sample_queries:
        print(f"  • {q}")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break
        print(f"Bot: {generate_response(user_input)}")


if __name__ == "__main__":
    main()
