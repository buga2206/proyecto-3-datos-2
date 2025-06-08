import socket
import os
import base64
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import raid5  # nuestro módulo de split_data

app = Flask(__name__)
CORS(app)

client_connected = False
registered_nodes = {}
ALLOWED_NODE_IDS = ['1','2','3','4']
METADATA_PATH = 'metadata.json'

# --- Inicializar metadata.json si no existe ---
if not os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, 'w') as f:
        json.dump({'files': []}, f)

# --- endpoints existentes ---

@app.route('/api/connect', methods=['POST'])
def connect():
    global client_connected
    if client_connected:
        return jsonify({'status':'fail','msg':'Ya hay un cliente conectado'}), 409
    client_connected = True
    return jsonify({'status':'ok','msg':'Cliente conectado'}), 200

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    global client_connected
    if not client_connected:
        return jsonify({'status':'fail','msg':'No hay cliente conectado'}), 409
    client_connected = False
    return jsonify({'status':'ok','msg':'Cliente desconectado'}), 200

@app.route('/api/nodes/register', methods=['POST'])
def register_node():
    info = request.get_json() or {}
    nid = str(info.get('id',''))
    if nid not in ALLOWED_NODE_IDS:
        return jsonify({'status':'fail','msg':f'ID {nid} inválido'}), 400
    if nid in registered_nodes:
        return jsonify({'status':'fail','msg':f'Slot {nid} ya ocupado'}), 409
    host = info.get('host'); port = info.get('port')
    for ex in registered_nodes.values():
        if ex['host']==host and ex['port']==port:
            return jsonify({'status':'fail','msg':'Host y puerto ya registrados'}), 409
    registered_nodes[nid] = info
    print(f"[NODE] Registrado nodo {nid} → {host}:{port}")
    return jsonify({'status':'ok','msg':f'Registrado nodo {nid}'}), 200

# --- nuevo endpoint de comandos ---

@app.route('/api/command', methods=['POST'])
def command():
    if not client_connected:
        return jsonify({'status':'fail','msg':'Cliente NO conectado'}), 409

    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'status':'fail','msg':'JSON no recibido'}), 400

    cmd = payload.get('cmd','')
    # === UPLOAD ===
    if cmd == 'upload':
        # validar nodos
        if len(registered_nodes) != 4:
            return jsonify({'status':'fail','msg':'Se requieren 4 DiskNodes'}), 409
        # salud
        for nid, info in registered_nodes.items():
            url = f"http://{info['host']}:{info['port']}/api/health"
            try:
                r = requests.get(url, timeout=3)
                if r.status_code != 200: raise
            except:
                return jsonify({'status':'fail','msg':f'Nodo {nid} no responde'}), 503
        # base64 → bytes
        name = payload.get('name','').strip()
        b64  = payload.get('data','')
        if not name or not b64:
            return jsonify({'status':'fail','msg':'Faltan "name" o "data"'}), 400
        try:
            data = base64.b64decode(b64)
        except:
            return jsonify({'status':'fail','msg':'Base64 inválido'}), 400
        filename = os.path.basename(name)
        # RAID-5 split
        parts = raid5.split_data(data, data_shards=3)
        # enviar fragmentos
        for nid, fragment in parts.items():
            info = registered_nodes[nid]
            url = f"http://{info['host']}:{info['port']}/upload/{filename}.part{nid}.bin"
            try:
                r = requests.put(url, data=fragment, timeout=5)
                if r.status_code != 200:
                    raise Exception(r.text)
            except Exception as e:
                return jsonify({'status':'fail','msg':f'Error en nodo {nid}: {e}'}), 502
        # actualizar metadata
        with open(METADATA_PATH,'r+') as f:
            meta = json.load(f)
            if filename not in meta['files']:
                meta['files'].append(filename)
                f.seek(0); json.dump(meta,f); f.truncate()
        return jsonify({'status':'ok','msg':'PDF fragmentado y distribuido'}), 200

    # === LIST ===
    if cmd == 'list':
        with open(METADATA_PATH,'r') as f:
            meta = json.load(f)
        return jsonify({'status':'ok','files': meta.get('files',[]) }), 200

    # otros comandos…
    return jsonify({'status':'fail','msg':'Comando no implementado'}), 400

if __name__=='__main__':
    host_ip = socket.gethostbyname(socket.gethostname())
    print("🚀 Server escuchando en:")
    print("    • http://0.0.0.0:8000")
    print(f"    • http://{host_ip}:8000\n")
    app.run(host='0.0.0.0', port=8000, debug=True)
