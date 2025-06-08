import sys
import os
import socket
import requests
import xml.etree.ElementTree as ET
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

def load_config(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return {
        'host':         root.findtext('host'),
        'port':         int(root.findtext('port')) if root.findtext('port') else None,
        'storage_path': root.findtext('storage_path'),
        'ctrl_host':    root.findtext('controller/host'),
        'ctrl_port':    int(root.findtext('controller/port')) if root.findtext('controller/port') else None,
    }

def start_file_server(storage_path, bind_host, bind_port):
    os.chdir(storage_path)
    httpd = ThreadingHTTPServer((bind_host, bind_port), SimpleHTTPRequestHandler)
    print(f"📂 Sirviendo '{storage_path}' en http://{bind_host}:{bind_port}/")
    httpd.serve_forever()

def main():
    if len(sys.argv) != 2:
        print("Uso: python disknode.py <config.xml>")
        sys.exit(1)

    cfg = load_config(sys.argv[1])
    for key in ('host','port','storage_path','ctrl_host','ctrl_port'):
        if not cfg.get(key):
            print(f"❌ Faltando configuración '{key}' en {sys.argv[1]}")
            sys.exit(1)

    # Asegurarse de que el directorio de almacenamiento existe
    if not os.path.isdir(cfg['storage_path']):
        try:
            os.makedirs(cfg['storage_path'], exist_ok=True)
        except OSError as e:
            print("❌ No pude crear storage_path:", e)
            sys.exit(1)

    ctrl_url = f"http://{cfg['ctrl_host']}:{cfg['ctrl_port']}/api/nodes/register"
    # Detectar IP real de este host
    my_ip = socket.gethostbyname(socket.gethostname())

    # Intentar slots 1–4
    for nid in ['1','2','3','4']:
        payload = {
            "id":           nid,
            "host":         my_ip,
            "port":         cfg['port'],
            "storage_path": cfg['storage_path']
        }
        try:
            resp = requests.post(ctrl_url, json=payload, timeout=5)
        except Exception as e:
            print("❌ Error conectando al controller:", e)
            sys.exit(1)

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code == 200:
            print(f"✅ Me he registrado como DiskNode {nid}")
            start_file_server(cfg['storage_path'], cfg['host'], cfg['port'])
            return
        else:
            msg = data.get('msg', '<sin mensaje>')
            print(f"⚠️  Slot {nid} rechazado: {msg}")

    print("❌ Ningún slot disponible. Saliendo.")
    sys.exit(1)

if __name__=='__main__':
    main()
