import os
import json
import urllib.request
from flask import Flask, render_template, request, jsonify
from quiz_data import QUIZ_QUESTOES
import random

SUPABASE_URL = "https://xotwhuluhqdlsqybcsfl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvdHdodWx1Z2hkbHNxeWJjc2ZsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODc4ODM5MCwiZXhwIjoyMTA0MzY0MzkwfQ.G17kS37ihL2sByHskeUGSVhzZHryEAaQBb3Jhl9rJTo"

app = Flask(__name__, template_folder='../templates')

def supabase_request(endpoint, method="GET", data=None):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    req_data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            return json.loads(body) if body else []
    except Exception as e:
        print(f"Erro Supabase REST: {e}")
        return None

# Rotas de navegação principais
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flick')
def flick_page():
    return render_template('flick.html')

@app.route('/tracking')
def tracking_page():
    return render_template('tracking.html')

@app.route('/crosshair')
def crosshair_page():
    return render_template('crosshair.html')

@app.route('/curiosidades')
def curiosidades_page():
    return render_template('curiosidades.html')

# --- ROTAS DE RANKING USANDO API REST DIRETA ---

@app.route('/api/ranking/<mode>', methods=['GET'])
def get_ranking(mode):
    try:
        endpoint = f"rankings?select=*&order=score.desc,accuracy.desc&limit=50"
        data = supabase_request(endpoint, method="GET")
        
        if isinstance(data, list):
            filtered = [row for row in data if row.get('mode') == mode]
            return jsonify(filtered[:10])
            
        return jsonify([])
    except Exception as e:
        print(f"Erro ao buscar ranking: {e}")
        return jsonify([])
@app.route('/api/ranking/<mode>', methods=['POST'])
def save_score(mode):
    req_data = request.json
    player_name = req_data.get('name', 'Anônimo').strip()
    score = req_data.get('score', 0)
    accuracy = req_data.get('accuracy', 0)
    
    if not player_name:
        player_name = 'Anônimo'
        
    payload = {
        "mode": mode,
        "name": player_name,
        "score": score,
        "accuracy": accuracy,
        "time": 0
    }
    
    result = supabase_request("rankings", method="POST", data=payload)
    if result is not None:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Falha ao salvar no banco"}), 500

@app.route('/api/ranking/clear/<mode>', methods=['POST'])
def clear_ranking(mode):
    endpoint = f"rankings?mode=eq.{mode}"
    try:
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        req = urllib.request.Request(url, headers=headers, method="DELETE")
        urllib.request.urlopen(req)
        return jsonify({"status": "cleared"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')

@app.route('/api/quiz/questions/<mode>', methods=['GET'])
def get_quiz_questions(mode):
    selected = random.sample(QUIZ_QUESTOES, min(10, len(QUIZ_QUESTOES)))
    return jsonify(selected)

@app.route('/api/ranking/quiz', methods=['GET'])
def get_quiz_ranking():
    try:
        endpoint = "rankings?mode=eq.quiz&order=score.desc,time.asc&limit=10"
        data = supabase_request(endpoint, method="GET")
        return jsonify(data if data is not None else [])
    except Exception as e:
        return jsonify([])

@app.route('/api/ranking/quiz', methods=['POST'])
def save_quiz_score():
    req_data = request.json
    player_name = req_data.get('name', 'Anônimo').strip()
    score = req_data.get('score', 0)
    time_spent = req_data.get('time', 0)
    accuracy = int((score / 10) * 100)
    
    if not player_name:
        player_name = 'Anônimo'
        
    payload = {
        "mode": 'quiz',
        "name": player_name,
        "score": score,
        "accuracy": accuracy,
        "time": time_spent
    }
    
    result = supabase_request("rankings", method="POST", data=payload)
    if result is not None:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Falha ao salvar no banco"}), 500