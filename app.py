from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

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

# ✅ Ruta para obtener todas las fechas únicas
@app.route('/fechas_eventos', methods=['GET'])
def obtener_fechas_eventos():
    try:
        docs = db.collection('eventos').stream()
        fechas = list({doc.to_dict().get('fecha') for doc in docs if 'fecha' in doc.to_dict()})
        return jsonify({'fechas': fechas}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Ruta para obtener datos del evento por fecha
@app.route('/datos_evento', methods=['POST'])
def datos_evento():
    data = request.get_json()
    fecha = data.get('fecha')

    try:
        query = db.collection('eventos').where('fecha', '==', fecha)
        resultados = query.stream()
        datos = [doc.to_dict() for doc in resultados]
        return jsonify({'datos': datos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Ruta para actualizar el abono de un evento por fecha
@app.route('/actualizar_abono', methods=['POST'])
def actualizar_abono():
    data = request.get_json()
    fecha = data.get('fecha')
    abono = data.get('abono', 0)

    try:
        docs = db.collection('eventos').where('fecha', '==', fecha).stream()
        for doc in docs:
            evento = doc.to_dict()
            abono_actual = evento.get('cantidadAbono', 0)
            nuevo_abono = abono_actual + abono
            db.collection('eventos').document(doc.id).update({'cantidadAbono': nuevo_abono})
        return jsonify({'mensaje': 'Abono actualizado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ CORRECTO
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)