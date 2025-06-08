import socket
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

client_connected = False
registered_nodes = {}
ALLOWED_NODE_IDS = ['1','2','3','4']

@app.route('/api/connect', methods=['POST'])
def connect():
    global client_connected
    if client_connected:
        return jsonify({'status':'fail', 'msg':'Ya hay un cliente conectado'}), 409
    client_connected = True
    return jsonify({'status':'ok', 'msg':'Cliente conectado'}), 200

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    global client_connected
    if not client_connected:
        return jsonify({'status':'fail', 'msg':'No hay cliente conectado'}), 409
    client_connected = False
    return jsonify({'status':'ok', 'msg':'Cliente desconectado'}), 200

@app.route('/api/nodes/register', methods=['POST'])
def register_node():
    """
    Espera un JSON:
      { "id": <1–4>, "host":"x.x.x.x", "port":<int>, "storage_path":"..." }
    Responde 200 si id ∈ {1,2,3,4} y slot libre,
    400 si el id no es válido, 409 si el slot ya está ocupado
      o si ya hay un DiskNode registrado en ese host:port.
    """
    info = request.get_json() or {}
    nid  = str(info.get('id',''))

    # id válido
    if nid not in ALLOWED_NODE_IDS:
        return jsonify({'status':'fail','msg':f'ID {nid} inválido'}), 400

    # slot de ID libre
    if nid in registered_nodes:
        return jsonify({'status':'fail','msg':f'Slot {nid} ya ocupado'}), 409

    # evitar duplicar host+port
    host = info.get('host')
    port = info.get('port')
    for existing in registered_nodes.values():
        if existing.get('host') == host and existing.get('port') == port:
            return jsonify({'status':'fail','msg':'Host y puerto ya registrados'}), 409

    # todo ok: registrar
    registered_nodes[nid] = info
    print(f"[NODE] Registrado nodo {nid} → {host}:{port}")
    return jsonify({'status':'ok','msg':f'Registrado nodo {nid}'}), 200

if __name__=='__main__':
    host_ip = socket.gethostbyname(socket.gethostname())
    print("🚀 Server escuchando en:")
    print("    • http://0.0.0.0:8000")
    print(f"    • http://{host_ip}:8000\n")
    app.run(host='0.0.0.0', port=8000, debug=True)
