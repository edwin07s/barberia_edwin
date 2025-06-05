from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Cargar credenciales desde variable de entorno
json_cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
cred = credentials.Certificate(json.loads(json_cred))
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def inicio():
    return 'Servidor Flask conectado a Firebase correctamente'

@app.route('/precios', methods=['GET'])
def obtener_precios():
    try:
        docs = db.collection('precios').stream()
        precios = []
        for doc in docs:
            data = doc.to_dict()
            motivo = data.get('motivo')
            if motivo in ['foto', 'video']:
                precios.append({
                    'id': doc.id,
                    'motivo': motivo,
                    'precio': data.get('precio', 0),
                    'tiempo': data.get('tiempo', 1)  # opcional
                })
        return jsonify({'precios': precios}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/calcular_precio', methods=['POST'])
def calcular_precio():
    data = request.get_json()
    motivo = data.get('motivo')
    cantidad = data.get('cantidad', 1)

    try:
        query = db.collection('precios').where('motivo', '==', motivo).stream()
        precio_unitario = 0
        for doc in query:
            precio_unitario = doc.to_dict().get('precio', 0)
            break  # solo uno
        total = precio_unitario * cantidad
        return jsonify({'total': total}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)