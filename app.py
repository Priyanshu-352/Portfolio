from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
import os
import difflib
import html
import re
from flask_cors import CORS
load_dotenv()
app = Flask(__name__)
CORS(app)
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Load CSV ONCE (not every request)
csv_path = os.path.join(os.path.dirname(__file__), 'data.csv')
try:
    df = pd.read_csv(csv_path)
    df['question'] = df['question'].astype(str)
    df['answer'] = df['answer'].astype(str)
except Exception as e:
    print("CSV load error:", e)
    df = pd.DataFrame(columns=['question', 'answer'])

# ------------------------------------------------------------------
# ANTI-HALLUCINATION GUARDRAIL (strict):
# The bot is forbidden from making up an answer. If a user question
# does not confidently match the knowledge base (data.csv), the bot
# must NOT reply with a guessed answer. Instead it replies with:
#     "I did get that, did you mean this?"
# followed by the closest-matching options and their closeness
# probability, so the user can pick/refine. Everything is computed
# deterministically from the CSV (no free-form model reply).
# ------------------------------------------------------------------
CONFIDENT_MATCH = 0.85   # score >= this  -> answer directly from CSV
SHOW_OPTIONS_MIN = 0.30  # score >= this  -> show closest-probability options
TOP_N = 4                # how many closest options to offer

# Words that carry no meaning -> ignored so real keywords (skills, email,
# degree...) dominate the match. This fixes difflib being fooled by filler
# words such as "what", "his", "is" (e.g. "what are his skills" must match
# "skills?", NOT "what is his name").
STOPWORDS = set(
    "a an the and or of in on for to with what which who whom whose how why "
    "when where is are was were do does did i me my your his her its our their "
    "he she it be been being you us them as at by from about".split()
)

def _tokens(text):
    """Lowercase alphanumeric word tokens (punctuation removed)."""
    return set(re.findall(r"[a-zA-Z0-9]+", (text or '').lower()))

def keyword_overlap(query, question):
    """Fraction of the question's content words that appear in the query.
    0..1. 1.0 means the question's real keywords are all present."""
    q_content = _tokens(question) - STOPWORDS
    query_content = _tokens(query) - STOPWORDS
    if not q_content:
        return 0.0
    return len(q_content & query_content) / len(q_content)

def score_match(query, question):
    """Best of character-level similarity and keyword overlap, so that
    keyword matches (skills -> skills?) rank above filler-word matches."""
    char = difflib.SequenceMatcher(None, query.lower(), question.lower()).ratio()
    kw = keyword_overlap(query, question)
    return max(char, kw)

# Do NOT change the behaviour of this string unless you accept the
# risk of letting the model hallucinate. It is enforced strictly.
STRICT_PROMPT = (
    "You are a portfolio assistant. You are ORDERS OF MAGNITUDE MORE LIKELY "
    "TO BE WRONG THAN RIGHT. STRICT RULE: NEVER answer a user question yourself. "
    "If the user's message closely matches one of the CSV questions (score >= 0.85) "
    "reply ONLY with that CSV answer. Otherwise reply ONLY with: "
    "'I did get that, did you mean this?' followed by the closest CSV questions "
    "and their match percentages. DO NOT reply anything else. DO NOT guess, "
    "DO NOT invent, DO NOT use general knowledge."
)

def get_top_matches(df, query, top_n=TOP_N):
    query = (query or '').lower().strip()
    scored = []
    for _, row in df.iterrows():
        q = row['question']
        score = score_match(query, q) if q and q.strip() else 0
        if score > 0:  # keep only questions that at least partially relate
            scored.append({
                'question': row['question'],
                'answer': row['answer'],
                'score': score
            })
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_n]

def build_disambiguation(matches):
    """Build the 'I did get that, did you mean this?' reply with closest options."""
    lines = ["I did get that, did you mean this?"]
    for i, m in enumerate(matches, 1):
        pct = round(max(m['score'], 0) * 100)
        q = html.escape(m['question'])
        lines.append(f"{i}. {q} — <b>{pct}%</b> closest")
    lines.append("Type a number above or rephrase — I won't guess an answer.")
    return "<br>".join(lines)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = (data.get('message') or '').strip()
    if not user_message:
        return jsonify({'reply': "I did get that, did you mean this? Please type your question clearly."})

    csv_path = os.path.join(os.path.dirname(__file__), 'data.csv')
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['question', 'answer'])

    # 1) Confident CSV match -> answer directly from knowledge base
    matches = get_top_matches(df, user_message)
    best = matches[0] if matches else None
    best_score = best['score'] if best else 0

    if best_score >= CONFIDENT_MATCH:
        return jsonify({'reply': best['answer']})

    # 2) Reasonably close -> anti-hallucination disambiguation
    #    (deterministic, computed from CSV - no free-form reply)
    if matches and best_score >= SHOW_OPTIONS_MIN:
        return jsonify({
            'reply': build_disambiguation(matches),
            'options': [
                {
                    'index': i,
                    'question': m['question'],
                    'score': round(max(m['score'], 0), 2)
                }
                for i, m in enumerate(matches, 1)
            ]
        })

    # 3) Nothing close -> do NOT guess; clearly say we didn't get it
    return jsonify({
        'reply': ("I did get that, did you mean this? I couldn't find a close match in "
                  "my portfolio data. Try asking about my skills, projects, education, "
                  "or experience.")
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

