

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FAQ_PAIRS: list[tuple[str, str]] = [
    # Timing
    ("What are the institute timings?",
     "Our institute is open from 9 AM to 5 PM, Monday to Friday."),
    ("What are the office hours?",
     "Our institute is open from 9 AM to 5 PM, Monday to Friday."),
    ("When does the institute open?",
     "Our institute is open from 9 AM to 5 PM, Monday to Friday."),

    # Fees
    ("What are the tuition fees?",
     "Tuition fees vary by course. Please refer to the official fee structure on our website."),
    ("How much does it cost to study here?",
     "Tuition fees vary by course. Please refer to the official fee structure on our website."),
    ("What is the fee payment schedule?",
     "Tuition fees vary by course. Please refer to the official fee structure on our website."),

    # Contact
    ("How can I contact the institute?",
     "You can reach us at contact@institute.com or call 123-456-7890."),
    ("What is the phone number of the institute?",
     "You can reach us at contact@institute.com or call 123-456-7890."),
    ("What is the email address?",
     "You can reach us at contact@institute.com or call 123-456-7890."),

    # Admission
    ("How do I apply for admission?",
     "Admissions are based on eligibility criteria. Applications are available on our website."),
    ("What is the admission process?",
     "Admissions are based on eligibility criteria. Applications are available on our website."),
    ("When do admissions open?",
     "Admissions are based on eligibility criteria. Applications are available on our website."),

    # Courses
    ("What courses does the institute offer?",
     "We offer undergraduate and postgraduate programs across Engineering, Management, and Sciences."),
    ("Which programs are available?",
     "We offer undergraduate and postgraduate programs across Engineering, Management, and Sciences."),
    ("What degrees can I pursue here?",
     "We offer undergraduate and postgraduate programs across Engineering, Management, and Sciences."),

    # Location
    ("Where is the institute located?",
     "The institute is in the city centre with easy access to public transport."),
    ("What is the address of the college?",
     "The institute is in the city centre with easy access to public transport."),
    ("How do I reach the campus?",
     "The institute is in the city centre with easy access to public transport."),

    # Faculty
    ("Who are the teachers at the institute?",
     "Our faculty consists of experienced professionals and qualified academics in every field."),
    ("Tell me about the faculty.",
     "Our faculty consists of experienced professionals and qualified academics in every field."),
    ("Are the professors qualified?",
     "Our faculty consists of experienced professionals and qualified academics in every field."),

    # Placement
    ("Does the institute have a placement cell?",
     "We have an active placement cell supporting students with internships and job opportunities."),
    ("What are the job placement opportunities?",
     "We have an active placement cell supporting students with internships and job opportunities."),
    ("How is the recruitment record?",
     "We have an active placement cell supporting students with internships and job opportunities."),

    # Hostel
    ("Is hostel accommodation available?",
     "Separate hostel facilities are available for boys and girls with meals and Wi-Fi."),
    ("Does the college provide accommodation?",
     "Separate hostel facilities are available for boys and girls with meals and Wi-Fi."),
    ("Are there dormitories on campus?",
     "Separate hostel facilities are available for boys and girls with meals and Wi-Fi."),

    # Scholarship
    ("Are scholarships available?",
     "Scholarships are available for eligible students based on merit and category norms."),
    ("Is there any financial aid?",
     "Scholarships are available for eligible students based on merit and category norms."),
    ("How can I get a fee waiver?",
     "Scholarships are available for eligible students based on merit and category norms."),

    # Exams
    ("When are the examinations held?",
     "Exams are conducted per the academic calendar and university guidelines."),
    ("What is the exam schedule?",
     "Exams are conducted per the academic calendar and university guidelines."),
    ("How are students assessed?",
     "Exams are conducted per the academic calendar and university guidelines."),

    # Library
    ("What facilities does the library offer?",
     "Our library has books, journals, and digital resources open 8 AM – 8 PM on weekdays."),
    ("Is there a reading room?",
     "Our library has books, journals, and digital resources open 8 AM – 8 PM on weekdays."),

    # Transport
    ("Does the institute provide transport?",
     "Institute bus services run from major city locations. Contact the transport office for routes."),
    ("Is there a college bus service?",
     "Institute bus services run from major city locations. Contact the transport office for routes."),
]

DEFAULT_RESPONSE = "No relevant answer found. Please contact the administration for further help."
SIMILARITY_THRESHOLD = 0.20   # adjust between 0.0 – 1.0


# ---------------------------------------------------------------------------
# 2.  BUILD TF-IDF MODEL AT MODULE LOAD
# ---------------------------------------------------------------------------
def _preprocess(text: str) -> str:
    """Lowercase and strip punctuation."""
    return re.sub(r"[^\w\s]", "", text.lower())


# Extract just the questions for vectorisation
_questions = [_preprocess(q) for q, _ in FAQ_PAIRS]
_answers   = [a for _, a in FAQ_PAIRS]

_vectorizer = TfidfVectorizer()
_tfidf_matrix = _vectorizer.fit_transform(_questions)   # shape: (n_faqs, n_terms)


# ---------------------------------------------------------------------------
# 3.  RETRIEVAL FUNCTION
# ---------------------------------------------------------------------------
def get_answer(user_query: str) -> tuple[str, float]:
    """
    Return (best_answer, similarity_score).
    If max similarity < SIMILARITY_THRESHOLD, returns the default message.
    """
    query_vec = _vectorizer.transform([_preprocess(user_query)])
    similarities = cosine_similarity(query_vec, _tfidf_matrix).flatten()

    best_idx   = similarities.argmax()
    best_score = float(similarities[best_idx])

    if best_score < SIMILARITY_THRESHOLD:
        return DEFAULT_RESPONSE, best_score

    return _answers[best_idx], best_score


# ---------------------------------------------------------------------------
# 4.  COMMAND-LINE DEMO
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("   TF-IDF Institute FAQ Chatbot  (type 'quit' to exit)")
    print(f"   Similarity threshold: {SIMILARITY_THRESHOLD}")
    print("=" * 60)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Bot: Goodbye! Have a great day.")
            break

        answer, score = get_answer(user_input)
        print(f"Bot: {answer}")
        print(f"     [similarity score: {score:.4f}]")


if __name__ == "__main__":
    main()
