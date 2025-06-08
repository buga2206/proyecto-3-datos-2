from flask import Flask, send_from_directory
import threading, webbrowser

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('static', 'interface.html')

if __name__ == '__main__':
    port = 5000
    threading.Timer(1.0, lambda: webbrowser.open(f"http://0.0.0.0:{port}")).start()
    app.run(host='0.0.0.0', port=port, debug=False)
