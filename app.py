import os
from flask import Flask, render_template, request, jsonify
from quiz_data import QUIZ_QUESTOES
import random
from google import genai
from supabase import create_client, Client


# Configuração do Supabase
SUPABASE_URL = "https://xotwhuluhqdlsqybcsfl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvdHdodWx1Z2hkbHNxeWJjc2ZsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODc4ODM5MCwiZXhwIjoyMTA0MzY0MzkwfQ.G17kS37ihL2sByHskeUGSVhzZHryEAaQBb3Jhl9rJTo"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

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

# --- ROTAS DE RANKING USANDO SUPABASE ---

@app.route('/api/ranking/<mode>', methods=['GET'])
def get_ranking(mode):
    try:
        # Busca no Supabase ordenado por pontuação e precisão
        response = supabase.table('rankings') \
            .select('*') \
            .eq('mode', mode) \
            .order('score', desc=True) \
            .order('accuracy', desc=True) \
            .limit(10) \
            .execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify([])

@app.route('/api/ranking/<mode>', methods=['POST'])
def save_score(mode):
    req_data = request.json
    player_name = req_data.get('name', 'Anônimo').strip()
    score = req_data.get('score', 0)
    accuracy = req_data.get('accuracy', 0)
    
    if not player_name:
        player_name = 'Anônimo'
        
    try:
        supabase.table('rankings').insert({
            "mode": mode,
            "name": player_name,
            "score": score,
            "accuracy": accuracy,
            "time": 0
        }).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ranking/clear/<mode>', methods=['POST'])
def clear_ranking(mode):
    try:
        supabase.table('rankings').delete().eq('mode', mode).execute()
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
        response = supabase.table('rankings') \
            .select('*') \
            .eq('mode', 'quiz') \
            .order('score', desc=True) \
            .order('time', desc=False) \
            .limit(10) \
            .execute()
        return jsonify(response.data)
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
        
    try:
        supabase.table('rankings').insert({
            "mode": 'quiz',
            "name": player_name,
            "score": score,
            "accuracy": accuracy,
            "time": time_spent
        }).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500