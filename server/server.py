from flask import Flask, request, jsonify
from flask_cors import CORS
import socket

app = Flask(__name__)
CORS(app)

total_connections = {"active": False}

@app.route('/api/connect', methods=['POST'])
def connect():
    if not total_connections['active']:
        total_connections['active'] = True
        return jsonify({"status": "ok", "msg": "Servidor conectado correctamente."}), 200
    else:
        return jsonify({"status": "fail", "msg": "Ya hay una conexión activa."}), 403

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    total_connections['active'] = False
    return jsonify({"status": "ok", "msg": "Servidor desconectado."}), 200

@app.route('/api/command', methods=['POST'])
def handle_command():
    if not total_connections['active']:
        return jsonify({"status": "fail", "msg": "No hay conexión activa."}), 403

    data = request.get_json()
    cmd = data.get('cmd')
    if not cmd:
        return jsonify({"status": "fail", "msg": "Comando no proporcionado."}), 400


    return jsonify({"status": "ok", "msg": f"Comando '{cmd}' recibido correctamente."}), 200

if __name__ == '__main__':
    # Detectar IP local para mostrar al arrancar
    host_ip = socket.gethostbyname(socket.gethostname())
    print(f"Servidor escuchando en:")
    print(f"  http://localhost:8000")
    print(f"  http://{host_ip}:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)