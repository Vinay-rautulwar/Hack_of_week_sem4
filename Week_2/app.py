# python app.py
# Plz help me find the best data engineering course in the system.


from flask import Flask, render_template, request
import string

app = Flask(__name__)

STOPWORDS = {
    "the", "is", "am", "are", "was", "were", "a", "an", "and", "or",
    "to", "of", "in", "on", "for", "with", "as", "by", "at", "from",
    "this", "that", "it", "be", "have", "has", "had"
}

SPELLING_NORMALIZATION = {
    "pls": "please",
    "plz": "please",
    "u": "you",
    "ur": "your",
    "thx": "thanks",
    "cant": "cannot",
    "wont": "will not"
}

def preprocess_query(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()
    words = [SPELLING_NORMALIZATION.get(word, word) for word in words]
    tokens = [word for word in words if word not in STOPWORDS]
    return tokens

@app.route("/", methods=["GET", "POST"])
def index():
    processed_tokens = None

    if request.method == "POST":
        query = request.form.get("query")
        processed_tokens = preprocess_query(query)

    return render_template("index.html", tokens=processed_tokens)

if __name__ == "__main__":
    app.run(debug=True)
