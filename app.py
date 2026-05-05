from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
import os
import difflib
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

def get_csv_match(df, query):
    best_score = 0
    best_answer = None
    for _, row in df.iterrows():
        score = difflib.SequenceMatcher(None, query.lower(), row['question'].lower()).ratio()
        if score > best_score:
            best_score = score
            best_answer = row['answer']
    return best_answer if best_score > 0.4 else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data.csv')
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['question', 'answer'])
    
    direct = get_csv_match(df, user_message)
    if direct:
        return jsonify({'reply': direct})
    
    prompt = f"Portfolio assistant. CSV: {df.to_csv(index=False)} User: {user_message} Use CSV match or 'Contact via Get in Touch.'"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        reply = response.text.strip()
    except:
        reply = "Sorry I am not capable for answering your query , please contact at priyanshusengupta284@gmail.com "
    
    return jsonify({'reply': reply})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

