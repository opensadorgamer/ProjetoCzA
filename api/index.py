import os
import json
import http.client
from flask import Flask, render_template, request, jsonify
from quiz_data import QUIZ_QUESTOES
import random

SUPABASE_URL = "xotwhuluhqdlsqybcsfl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvdHdodWx1Z2hkbHNxeWJjc2ZsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODc4ODM5MCxl-hwIjoyMTA0MzY0MzkwfQ.G17kS37ihL2sByHskeUGSVhzZHryEAaQBb3Jhl9rJTo"

app = Flask(__name__, template_folder='../templates')

def supabase_request(endpoint, method="GET", data=None):
    conn = http.client.HTTPSConnection(SUPABASE_URL, timeout=10)
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    body = json.dumps(data) if data else None
    
    try:
        conn.request(method, f"/rest/v1/{endpoint}", body=body, headers=headers)
        res = conn.getresponse()
        res_body = res.read().decode('utf-8')
        conn.close()
        
        if res.status >= 400:
            print(f"Erro Supabase HTTP {res.status}: {res_body}")
            return None
            
        return json.loads(res_body) if res_body else []
    except Exception as e:
        print(f"Erro conexao Supabase: {e}")
        conn.close()
        return None

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

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')

# --- ROTAS DE RANKING ---

@app.route('/api/ranking/<mode>', methods=['GET'])
def get_ranking(mode):
    try:
        endpoint = f"rankings?mode=eq.{mode}&order=score.desc,accuracy.desc&limit=10"
        data = supabase_request(endpoint, method="GET")
        return jsonify(data if data is not None else [])
    except Exception as e:
        print(f"Erro GET ranking {mode}: {e}")
        return jsonify([])

@app.route('/api/ranking/<mode>', methods=['POST'])
def save_score(mode):
    try:
        req_data = request.json or {}
        player_name = str(req_data.get('name', 'Anônimo')).strip()
        score = int(req_data.get('score', 0))
        accuracy = int(req_data.get('accuracy', 0))
        
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
            return jsonify({"status": "error", "message": "Falha ao gravar no banco"}), 500
    except Exception as e:
        print(f"Erro POST ranking {mode}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ranking/clear/<mode>', methods=['POST'])
def clear_ranking(mode):
    try:
        endpoint = f"rankings?mode=eq.{mode}"
        result = supabase_request(endpoint, method="DELETE")
        return jsonify({"status": "cleared"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
    try:
        req_data = request.json or {}
        player_name = str(req_data.get('name', 'Anônimo')).strip()
        score = int(req_data.get('score', 0))
        time_spent = int(req_data.get('time', 0))
        accuracy = int((score / 10) * 100) if score > 0 else 0
        
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
            return jsonify({"status": "error", "message": "Falha ao gravar no banco"}), 500
    except Exception as e:
        print(f"Erro POST quiz: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)