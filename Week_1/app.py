from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def faq_responder_with_synonyms(question):
    faqs = {
        "timing": ["timing", "time", "hours", "open"],
        "fees": ["fees", "tuition", "cost", "fee"],
        "contact": ["contact", "contacts", "phone", "email"],
        "admission": ["admission", "apply", "enroll", "registration"],
        "courses": ["courses", "programs", "degrees", "branches"],
        "location": ["location", "address", "where", "situated"],
        "faculty": ["faculty", "teachers", "professors", "staff"],
        "placement": ["placement", "job", "career", "recruitment"],
        "hostel": ["hostel", "hostels", "accommodation", "stay"],
        "scholarship": ["scholarship", "financial aid", "fee waiver"],
        "exams": ["exam", "exams", "test", "assessment"],
        "library": ["library", "books", "reading room"],
        "transport": ["transport", "bus", "travel"]
    }

    responses = {
        "timing": "Our institute is open from 9 AM to 5 PM, Monday to Friday.",
        "fees": "The tuition fees vary by course. Please refer to the official fee structure on our website.",
        "contact": "You can contact us at contact@institute.com or call 123-456-7890.",
        "admission": "Admissions are based on eligibility criteria and entrance requirements. Applications are available on our website.",
        "courses": "We offer undergraduate and postgraduate programs across multiple disciplines.",
        "location": "The institute is located in the city center with easy access to public transport.",
        "faculty": "Our faculty consists of experienced and qualified professionals in their respective fields.",
        "placement": "We have an active placement cell that supports students with internships and job opportunities.",
        "hostel": "Separate hostel facilities are available for boys and girls with basic amenities.",
        "scholarship": "Scholarships are available for eligible students based on merit and category norms.",
        "exams": "Examinations are conducted as per the academic calendar and university guidelines.",
        "library": "Our library is well-equipped with academic books, journals, and digital resources.",
        "transport": "Institute bus facilities are available from major locations in the city."
    }

    question = question.lower()

    for key, keywords in faqs.items():
        if any(keyword in question for keyword in keywords):
            return responses[key]

    return "I'm sorry, I can only answer common institute-related questions. Please contact the administration for further help."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_question = request.json.get("message")
    reply = faq_responder_with_synonyms(user_question)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
