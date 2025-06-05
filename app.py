from flask import Flask, jsonify
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
    return '✅ Servidor Flask conectado a Firebase correctamente'

# Ruta para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        docs = db.collection('usuarios').stream()
        usuarios = []

        for doc in docs:
            datos = doc.to_dict()
            datos['id'] = doc.id  # incluir el ID del documento si es necesario
            usuarios.append(datos)

        return jsonify(usuarios), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🔚 Ejecutar la app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)