

import re

# ---------------------------------------------------------------------------
# 1.  KNOWLEDGE BASE (shared with entity-recognition module concept)
# ---------------------------------------------------------------------------
EXAM_DB: dict[tuple[str, str], dict] = {
    ("1","CS"):{"date":"2025-05-10","time":"10:00 AM","room":"Hall A"},
    ("2","CS"):{"date":"2025-05-12","time":"10:00 AM","room":"Hall A"},
    ("3","CS"):{"date":"2025-05-14","time":"02:00 PM","room":"Lab 3"},
    ("4","CS"):{"date":"2025-05-16","time":"10:00 AM","room":"Hall B"},
    ("5","CS"):{"date":"2025-05-18","time":"10:00 AM","room":"Hall C"},
    ("6","CS"):{"date":"2025-05-20","time":"02:00 PM","room":"Hall C"},
    ("1","MATH"):{"date":"2025-05-11","time":"09:00 AM","room":"Hall A"},
    ("2","MATH"):{"date":"2025-05-13","time":"09:00 AM","room":"Hall A"},
    ("3","MATH"):{"date":"2025-05-15","time":"09:00 AM","room":"Hall B"},
    ("4","MATH"):{"date":"2025-05-17","time":"09:00 AM","room":"Hall B"},
    ("5","MATH"):{"date":"2025-05-19","time":"09:00 AM","room":"Hall C"},
    ("1","PHY"):{"date":"2025-05-12","time":"11:00 AM","room":"Hall A"},
    ("3","PHY"):{"date":"2025-05-16","time":"11:00 AM","room":"Lab 1"},
}

FEES_INFO: dict[str, str] = {
    "CS":   "Computer Science: ₹85,000/year",
    "MATH": "Mathematics: ₹72,000/year",
    "PHY":  "Physics: ₹70,000/year",
}

COURSE_ALIASES: dict[str, str] = {
    "cs":"CS","computer science":"CS","comp sci":"CS",
    "math":"MATH","maths":"MATH","mathematics":"MATH",
    "phy":"PHY","physics":"PHY",
}

WORD_TO_NUM: dict[str, str] = {
    "first":"1","second":"2","third":"3",
    "fourth":"4","fifth":"5","sixth":"6",
}

# ---------------------------------------------------------------------------
# 2.  CONVERSATION STATE
# ---------------------------------------------------------------------------
class ConversationState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.last_topic    = None   # "exam" | "fees" | "hostel" | None
        self.last_semester = None   # "3", "5", ...
        self.last_course   = None   # "CS", "MATH", ...
        self.last_intent   = None
        self.turns         = 0      # number of completed turns

    def update(self, topic=None, semester=None, course=None, intent=None):
        if topic    : self.last_topic    = topic
        if semester : self.last_semester = semester
        if course   : self.last_course   = course
        if intent   : self.last_intent   = intent
        self.turns += 1

    def summary(self) -> str:
        parts = []
        if self.last_topic   : parts.append(f"topic={self.last_topic}")
        if self.last_semester: parts.append(f"sem={self.last_semester}")
        if self.last_course  : parts.append(f"course={self.last_course}")
        return ", ".join(parts) if parts else "empty"


# ---------------------------------------------------------------------------
# 3.  ENTITY + INTENT EXTRACTION
# ---------------------------------------------------------------------------
def extract_semester(text: str) -> str | None:
    for pat in [r"\bsem(?:ester)?\s*(\d)\b", r"\b(\d)(?:st|nd|rd|th)?\s*sem\b",
                r"\b(first|second|third|fourth|fifth|sixth)\s*(?:year|sem(?:ester)?)\b"]:
        m = re.search(pat, text.lower())
        if m:
            return WORD_TO_NUM.get(m.group(1), m.group(1))
    return None

def extract_course(text: str) -> str | None:
    tl = text.lower()
    for alias, code in COURSE_ALIASES.items():
        if alias in tl:
            return code
    m = re.search(r"\b([A-Z]{2,5})\b", text)
    if m and m.group(1) not in {"SEM","FOR","THE","AND","WHEN","IS","WHAT"}:
        return m.group(1)
    return None

def classify_intent(text: str) -> str:
    tl = text.lower()
    if any(w in tl for w in ["exam","test","examin","timetable","schedule","date"]):
        return "exam"
    if any(w in tl for w in ["fee","fees","cost","tuition","payment"]):
        return "fees"
    if any(w in tl for w in ["hostel","accommodation","dorm","stay"]):
        return "hostel"
    if any(w in tl for w in ["placement","job","career","recruit"]):
        return "placement"
    if any(w in tl for w in ["hello","hi","hey"]):
        return "greeting"
    return "unknown"


# ---------------------------------------------------------------------------
# 4.  RESPONSE BUILDER
# ---------------------------------------------------------------------------
def exam_response(sem: str | None, course: str | None) -> str:
    if sem and course:
        info = EXAM_DB.get((sem, course))
        if info:
            return f"The SEM {sem} {course} exam is on {info['date']} at {info['time']} in {info['room']}."
        return f"No exam details found for SEM {sem} {course}. Please check the notice board."
    if sem and not course:
        available = sorted({c for s,c in EXAM_DB if s==sem})
        return f"For SEM {sem}, available courses are: {', '.join(available)}. Which one?"
    if course and not sem:
        available = sorted({s for s,c in EXAM_DB if c==course})
        return f"For {course}, I have data for semesters: {', '.join(available)}. Which semester?"
    return "Could you tell me the semester and course? e.g. 'SEM 5 CS exam'"

def fees_response(course: str | None) -> str:
    if course and course in FEES_INFO:
        return FEES_INFO[course]
    return "Fees vary by course. Available: " + ", ".join(FEES_INFO.values())


# ---------------------------------------------------------------------------
# 5.  MULTI-TURN CHATBOT
# ---------------------------------------------------------------------------
def chat(user_input: str, state: ConversationState) -> str:
    intent = classify_intent(user_input)
    sem    = extract_semester(user_input)
    course = extract_course(user_input)

    # --- Inherit context from previous turn when info is missing ---
    effective_sem    = sem    or state.last_semester
    effective_course = course or state.last_course
    effective_intent = intent if intent != "unknown" else state.last_intent

    print(f"  [state before: {state.summary()}]")
    print(f"  [extracted → intent={intent}, sem={sem}, course={course}]")
    print(f"  [effective → intent={effective_intent}, sem={effective_sem}, course={effective_course}]")

    # Update state
    state.update(
        topic    = effective_intent,
        semester = effective_sem,
        course   = effective_course,
        intent   = effective_intent,
    )

    # --- Generate response ---
    if effective_intent == "greeting":
        return "Hello! I can help with exams, fees, hostel, and placement. What would you like to know?"

    if effective_intent in {"exam", None} and (effective_sem or effective_course):
        return exam_response(effective_sem, effective_course)

    if effective_intent == "fees":
        return fees_response(effective_course)

    if effective_intent == "hostel":
        return "Hostel facilities are available for both boys and girls. Contact the hostel office for room allocation."

    if effective_intent == "placement":
        return "Our placement cell is active year-round. For details visit the placement portal or email placement@institute.edu."

    # Ask for clarification
    if state.last_topic:
        return f"I'm still not sure. Are you asking about {state.last_topic}? Could you be more specific?"

    return "I didn't understand that. Try asking about exams, fees, hostel, or placement."


# ---------------------------------------------------------------------------
# 6.  COMMAND-LINE DEMO
# ---------------------------------------------------------------------------
def main() -> None:
    state = ConversationState()
    print("=" * 60)
    print("   Multi-Turn Chatbot  (type 'reset' to clear context, 'quit' to exit)")
    print("=" * 60)
    print("\nTry a multi-turn conversation:")
    print("  You: When is the exam?")
    print("  You: For third year CS")
    print("  You: What about math?")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break
        if user_input.lower() == "reset":
            state.reset()
            print("Bot: Context cleared. Starting fresh!")
            continue
        response = chat(user_input, state)
        print(f"Bot: {response}")


if __name__ == "__main__":
    main()
