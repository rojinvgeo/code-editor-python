from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
import subprocess

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@app.route('/')
def serve_index():
    return send_from_directory(r'D:\code-editor\frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

@socketio.on('connect')
def handle_connect():
    print('WebSocket Client Connected')

@socketio.on('run_code')
def run_code(data):
    try:
        code = data['code']
        process = subprocess.Popen(['python', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode('utf-8')
        error = error.decode('utf-8')

        if error:
            emit('code_output', {'output': f'Error: {error}', 'error': True})
        else:
            emit('code_output', {'output': output, 'error': False})
    except Exception as e:
        emit('code_output', {'output': f'Error: {str(e)}', 'error': True})

@socketio.on('disconnect')
def handle_disconnect():
    print('WebSocket Client Disconnected')
    
if __name__ == '__main__':
    print("Running on http://localhost:5000/")
    socketio.run(app, host='localhost', port=5000, debug=True)