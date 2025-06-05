from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Inicializar la app Flask
app = Flask(__name__)
CORS(app)

# Cargar las credenciales desde la variable de entorno (en Render)
json_cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# Inicializar Firebase Admin con las credenciales
cred = credentials.Certificate(json.loads(json_cred))
firebase_admin.initialize_app(cred)

# Crear cliente de Firestore
db = firestore.client()

# Ruta de prueba
@app.route('/')
def inicio():
    return 'Servidor Flask conectado a Firebase correctamente'

# Ruta para obtener todos los usuarios
@app.route('/eventos', methods=['GET'])
def obtener_usuarios():
    try:
        docs = db.collection('eventos').stream()
        usuarios = []

        for doc in docs:
            datos = doc.to_dict()
            datos['id'] = doc.id  # incluir el ID del documento si es necesario
            usuarios.append(datos)

        return jsonify(eventos), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para obtener todas las fechas únicas en eventos
@app.route('/fechas_eventos', methods=['GET'])
def obtener_fechas_eventos():
    try:
        docs = db.collection('eventos').stream()
        fechas = list({doc.to_dict().get('fecha') for doc in docs if 'fecha' in doc.to_dict()})
        return jsonify({'fechas': fechas}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para obtener los datos de una fecha específica
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

# Ruta para actualizar cantidadAbono
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

# Ejecutar la app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)