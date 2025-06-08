import sys, os, socket, xml.etree.ElementTree as ET
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
import shutil

MAX_STORAGE = 1024 * 1024 * 100  # 100 MB por nodo (ajusta si quieres)

def load_config(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return {
        'host':         root.findtext('host'),
        'port':         int(root.findtext('port')),
        'storage_path': root.findtext('storage_path'),
        'ctrl_host':    root.findtext('controller/host'),
        'ctrl_port':    int(root.findtext('controller/port')),
    }

class DiskNodeHandler(SimpleHTTPRequestHandler):
    def _send_json(self, code, obj):
        import json
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == '/api/health':
            # salud
            return self._send_json(200, {'status':'ok'})
        return super().do_GET()

    def do_PUT(self):
        # ruta: /upload/<filename>
        if not self.path.startswith("/upload/"):
            return self.send_error(404)
        fname = unquote(self.path[len("/upload/"):])
        full_path = os.path.join(self.server.storage_path, fname)

        # lee contenido
        length = int(self.headers.get('Content-Length',0))
        content = self.rfile.read(length)

        # chequeo de espacio
        total = 0
        for root,_,files in os.walk(self.server.storage_path):
            for f in files:
                total += os.path.getsize(os.path.join(root,f))
        if total + length > MAX_STORAGE:
            return self._send_json(507, {'status':'fail','msg':'Espacio insuficiente'})

        # asegurar carpeta
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as out:
            out.write(content)

        return self._send_json(200, {'status':'ok','msg':f'Salvado {fname}'})

def start_file_server(cfg):
    os.chdir(cfg['storage_path'])
    handler = DiskNodeHandler
    server = ThreadingHTTPServer((cfg['host'], cfg['port']), handler)
    server.storage_path = cfg['storage_path']
    print(f"📂 Nodo sirviendo '{cfg['storage_path']}' en http://{cfg['host']}:{cfg['port']}/")
    server.serve_forever()

def main():
    if len(sys.argv)!=2:
        print("Uso: python disknode.py <config.xml>")
        sys.exit(1)
    cfg = load_config(sys.argv[1])
    for k in ('host','port','storage_path','ctrl_host','ctrl_port'):
        if not cfg.get(k):
            print("❌ Falta config", k); sys.exit(1)
    os.makedirs(cfg['storage_path'], exist_ok=True)

    # registrar en el máster
    ctrl = f"http://{cfg['ctrl_host']}:{cfg['ctrl_port']}/api/nodes/register"
    my_ip = socket.gethostbyname(socket.gethostname())
    for nid in ['1','2','3','4']:
        payload = {"id":nid,"host":my_ip,"port":cfg['port'],"storage_path":cfg['storage_path']}
        import requests
        try:
            r = requests.post(ctrl, json=payload, timeout=5)
            js = r.json()
        except Exception as e:
            print("❌ Error al registrar:", e); sys.exit(1)
        if r.status_code==200:
            print(f"✅ Nodo registrado como ID {nid}")
            start_file_server(cfg)
            return
        else:
            print(f"⚠️ Slot {nid} rechazado: {js.get('msg')}")

    print("❌ No hay slots disponibles. Saliendo.")
    sys.exit(1)

if __name__=='__main__':
    main()

