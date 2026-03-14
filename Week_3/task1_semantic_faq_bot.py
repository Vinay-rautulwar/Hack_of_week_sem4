
import re

# ---------------------------------------------------------------------------
# 1.  SYNONYM DICTIONARY
#     Maps every surface form → canonical topic key
# ---------------------------------------------------------------------------
SYNONYM_MAP: dict[str, str] = {
    # Timing / Hours
    "timing": "timing", "time": "timing", "hours": "timing",
    "open": "timing", "schedule": "timing", "when": "timing",

    # Fees / Payment
    "fees": "fees", "fee": "fees", "tuition": "fees",
    "payment": "fees", "cost": "fees", "price": "fees",
    "charges": "fees",

    # Contact
    "contact": "contact", "contacts": "contact", "phone": "contact",
    "email": "contact", "reach": "contact", "call": "contact",
    "helpline": "contact",

    # Admission / Enrollment
    "admission": "admission", "apply": "admission", "enroll": "admission",
    "registration": "admission", "joining": "admission",
    "application": "admission",

    # Courses / Programs
    "courses": "courses", "course": "courses", "programs": "courses",
    "program": "courses", "degrees": "courses", "degree": "courses",
    "branches": "courses", "subjects": "courses", "discipline": "courses",

    # Location / Address
    "location": "location", "address": "location", "where": "location",
    "situated": "location", "campus": "location", "place": "location",

    # Faculty / Staff
    "faculty": "faculty", "teachers": "faculty", "teacher": "faculty",
    "professors": "faculty", "professor": "faculty", "staff": "faculty",
    "lecturers": "faculty",

    # Placement / Jobs
    "placement": "placement", "job": "placement", "jobs": "placement",
    "career": "placement", "recruitment": "placement",
    "internship": "placement", "hire": "placement",

    # Hostel / Accommodation
    "hostel": "hostel", "hostels": "hostel", "accommodation": "hostel",
    "stay": "hostel", "dorm": "hostel", "dormitory": "hostel",
    "lodge": "hostel",

    # Scholarship / Financial Aid
    "scholarship": "scholarship", "scholarships": "scholarship",
    "financial": "scholarship", "aid": "scholarship",
    "waiver": "scholarship", "stipend": "scholarship",
    "grant": "scholarship",

    # Exams / Tests
    "exam": "exams", "exams": "exams", "test": "exams",
    "tests": "exams", "assessment": "exams", "examination": "exams",
    "evaluation": "exams",

    # Library
    "library": "library", "books": "library", "reading": "library",
    "journal": "library", "journals": "library", "resources": "library",

    # Transport / Bus
    "transport": "transport", "bus": "transport", "travel": "transport",
    "shuttle": "transport", "commute": "transport", "vehicle": "transport",
}

# ---------------------------------------------------------------------------
# 2.  FAQ RESPONSES  (one answer per canonical key)
# ---------------------------------------------------------------------------
FAQ_RESPONSES: dict[str, str] = {
    "timing":     "Our institute is open from 9 AM to 5 PM, Monday to Friday.",
    "fees":       "Tuition fees vary by course. Please refer to the official "
                  "fee structure on our website or contact the accounts office.",
    "contact":    "You can reach us at contact@institute.com or call 123-456-7890.",
    "admission":  "Admissions are based on eligibility criteria and entrance "
                  "requirements. Applications are available on our website.",
    "courses":    "We offer undergraduate and postgraduate programs across "
                  "multiple disciplines including Engineering, Management, and Sciences.",
    "location":   "The institute is located in the city centre with easy access "
                  "to public transport.",
    "faculty":    "Our faculty consists of experienced and qualified professionals "
                  "in their respective fields.",
    "placement":  "We have an active placement cell that supports students with "
                  "internships and full-time job opportunities.",
    "hostel":     "Separate hostel facilities are available for boys and girls "
                  "with basic amenities including Wi-Fi and meals.",
    "scholarship":"Scholarships are available for eligible students based on merit "
                  "and category norms. Visit the financial-aid portal for details.",
    "exams":      "Examinations are conducted as per the academic calendar and "
                  "university guidelines. Timetables are published on the notice board.",
    "library":    "Our library is well-equipped with academic books, journals, "
                  "and digital resources available 8 AM – 8 PM on weekdays.",
    "transport":  "Institute bus services are available from major locations in "
                  "the city. Contact the transport office for routes and timings.",
}

DEFAULT_RESPONSE = (
    "Sorry, I don't understand your question. "
    "Please contact the administration for further help."
)

# ---------------------------------------------------------------------------
# 3.  PREPROCESSING
# ---------------------------------------------------------------------------
def preprocess(text: str) -> list[str]:
    """Lowercase, strip punctuation, return list of tokens."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
    return text.split()


# ---------------------------------------------------------------------------
# 4.  SYNONYM NORMALIZATION + FAQ MATCHING
# ---------------------------------------------------------------------------
def faq_responder(question: str) -> str:
    """
    1. Preprocess the question.
    2. Replace every token with its canonical key (if found in SYNONYM_MAP).
    3. Return the first FAQ answer whose key appears in the normalised tokens.
    4. Return the default message if nothing matches.
    """
    tokens = preprocess(question)

    # Normalise: map each token to its canonical key (or keep as-is)
    normalised = [SYNONYM_MAP.get(token, token) for token in tokens]

    # Match against FAQ keys in order of definition
    for key in FAQ_RESPONSES:
        if key in normalised:
            return FAQ_RESPONSES[key]

    return DEFAULT_RESPONSE


# ---------------------------------------------------------------------------
# 5.  COMMAND-LINE DEMO
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 55)
    print("   Institute FAQ Chatbot  (type 'quit' to exit)")
    print("=" * 55)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Bot: Goodbye! Have a great day.")
            break

        response = faq_responder(user_input)
        print(f"Bot: {response}")


if __name__ == "__main__":
    main()
