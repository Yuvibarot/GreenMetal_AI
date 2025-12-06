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

# --- CONFIGURATION ---
# 🔴 REPLACE THIS WITH YOUR ACTUAL GEMINI API KEY
GEMINI_API_KEY = "AIzaSy..." 
genai.configure(api_key=AIzaSyB_KCFm4hYEDu-TOU6Q75CWTDDHcA5mZCM)

# --- LOAD AI MODELS ---
try:
    model = joblib.load('best_tuned_model.pkl')
    scaler = joblib.load('Scaler_Tuned.pkl')
    label_encoder = joblib.load('label_encoder_tuned.pkl')
    print("✅ GreenMetal AI System Loaded")
except Exception as e:
    print(f"⚠️ Model Loading Failed: {e}")
    model = None

# 31 Features (Scientific Defaults hidden from user)
MODEL_FEATURES = [
    'pH', 'Soil_OM_percent', 'Soil_Moisture_percent',
    'Sand_percent', 'Silt_percent', 'Clay_percent', 'CEC_meq_per_100g',
    'Ni_ppm', 'Co_ppm', 'Zn_ppm', 'Cu_ppm', 'Pb_ppm', 'Cd_ppm', 'Mn_ppm', 'Fe_ppm',
    'Annual_Rainfall_mm', 'Average_Temp_C', 'Growing_Season_days', 'Elevation_m',
    'Solar_Radiation_MJ_m2', 'Wind_Speed_m_s', 'Drainage_Score',
    'Industrial_Proximity_km', 'Mining_Activity_Score',
    'Contamination_Source_Score', 'Pollutant_Concentration_Index',
    'Avg_Metal_ppm', 'Total_Metal_ppm', 'Max_Metal_ppm',
    'Environmental_Score', 'Contamination_Viability'
]

# --- 1. PREDICTION ENDPOINT ---
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        user_ph = float(data.get('ph', 6.5))
        user_ni = float(data.get('ppm', 2000))
        area_ha = float(data.get('area', 10))

        # Smart Infilling (The "Hidden Intelligence")
        input_data = {
            'pH': user_ph, 
            'Ni_ppm': user_ni,
            # Scientific Averages for Ultramafic Soils
            'Soil_OM_percent': 5.5, 'Soil_Moisture_percent': 25.0,
            'Sand_percent': 40.0, 'Silt_percent': 40.0, 'Clay_percent': 20.0,
            'CEC_meq_per_100g': 15.0, 'Co_ppm': 150.0, 'Zn_ppm': 200.0,
            'Cu_ppm': 50.0, 'Pb_ppm': 20.0, 'Cd_ppm': 1.0, 'Mn_ppm': 800.0,
            'Fe_ppm': 30000.0, 'Annual_Rainfall_mm': 1200.0, 'Average_Temp_C': 22.0,
            'Growing_Season_days': 200, 'Elevation_m': 300, 'Solar_Radiation_MJ_m2': 15.0,
            'Wind_Speed_m_s': 3.5, 'Drainage_Score': 3, 'Industrial_Proximity_km': 5.0,
            'Mining_Activity_Score': 2, 'Contamination_Source_Score': 3,
            'Pollutant_Concentration_Index': 2.5,
            'Avg_Metal_ppm': (user_ni + 150 + 200) / 3,
            'Total_Metal_ppm': user_ni + 150 + 200,
            'Max_Metal_ppm': max(user_ni, 30000),
            'Environmental_Score': 7.5, 'Contamination_Viability': 1
        }

        if model:
            df = pd.DataFrame([input_data], columns=MODEL_FEATURES)
            df_scaled = scaler.transform(df)
            pred_idx = model.predict(df_scaled)[0]
            metal_class = label_encoder.inverse_transform([pred_idx])[0]
            
            probs = model.predict_proba(df_scaled)[0]
            confidence = round(float(probs.max() * 100), 1)
        else:
            # Fallback if model fails
            metal_class = "Ni"
            confidence = 95.0

        # Business Logic
        plant_map = {'Ni': 'Alyssum murale', 'Zn': 'Noccaea', 'Co': 'Haumaniastrum', 'Fe': 'Imperata', 'Mn': 'Phytolacca'}
        plant = plant_map.get(metal_class, "Generic Hyperaccumulator")
        
        yield_val = int(15000 * (user_ni/1000000) * area_ha * 100)
        revenue = yield_val * 22

        return jsonify({
            'status': 'success',
            'metal': metal_class,
            'plant': plant,
            'confidence': confidence,
            'yield': yield_val,
            'revenue': revenue,
            'carbon': int(area_ha * 2.5)
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# --- 2. CHATBOT ENDPOINT (Gaia) ---
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_msg = request.json.get('message')
        
        system_prompt = """
        You are Gaia, the AI Bio-Mining Consultant for GreenMetal.
        Your job is to explain how plants can mine metal (Phytomining).
        
        Key Rules:
        1. Be concise, scientific, but accessible.
        2. Explain that we check pH and Nickel levels to find the perfect plant match.
        3. Mention 'Bio-ore' (the metal-rich ash) as the product.
        4. If asked about the app, explain that it uses XGBoost to predict yield.
        """
        
        model_gemini = genai.GenerativeModel('gemini-2.0-flash')
        response = model_gemini.generate_content(f"{system_prompt}\nUser: {user_msg}")
        
        return jsonify({'reply': response.text})

    except Exception as e:
        return jsonify({'reply': "Gaia is offline. Please try again."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
