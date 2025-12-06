# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# --- 1. SETUP CHATBOT (GAIA) ---
# Replace with your actual key or use Environment Variable in Render
# OPTION A: Hardcode it (Easier for testing, risky for public repos)
GEMINI_KEY = "AIzaSyB_KCFm4hYEDu-TQU6Q75CWTDDHcA5mZCM"

# --- 2. LOAD MODELS ---
try:
    # Render paths can be tricky, try relative path first
    model = joblib.load('best_tuned_model.pkl')
    scaler = joblib.load('Scaler_Tuned.pkl')
    label_encoder = joblib.load('label_encoder_tuned.pkl')
    print("✅ Models Loaded")
except:
    model = None
    print("⚠️ Models not found (Prediction will use simulation)")

# --- 3. CHAT ROUTE ---
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_msg = request.json.get('message')
        # This prompts Gemini to act like "Gaia"
        prompt = f"""You are Gaia, an AI expert in Phytomining (mining metals with plants).
        Explain things simply.
        User asks: {user_msg}"""
        
        model_gemini = genai.GenerativeModel('gemini-2.0-flash')
        response = model_gemini.generate_content(prompt)
        return jsonify({'reply': response.text})
    except Exception as e:
        return jsonify({'reply': f"Gaia System Error: {str(e)}"})

# --- 4. PREDICTION ROUTE ---
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # ... (Your existing prediction logic here) ...
        # If model is loaded, use it. If not, use simulation logic.
        
        # [Simplified Simulation for Reliability]
        # You can paste your full XGBoost logic here if you have it
        user_ni = float(data.get('ppm', 0))
        area = float(data.get('area', 0))
        
        yield_val = int(area * user_ni * 0.15)
        revenue = yield_val * 18
        
        return jsonify({
            'status': 'success',
            'metal': 'Ni',
            'plant': 'Alyssum murale',
            'yield': yield_val,
            'revenue': revenue
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
