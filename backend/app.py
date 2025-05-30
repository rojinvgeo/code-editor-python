import eventlet
eventlet.monkey_patch()
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
import subprocess
import os


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
@app.route('/')
def serve_index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(frontend_dir, path)

@socketio.on('connect')
def handle_connect():
    print('WebSocket Client Connected')

@socketio.on('run_code')
def run_code(data):
    sid = request.sid
    try:
        code = data['code']

        def execute_code(code, sid):
            process = subprocess.Popen(['python', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            output = output.decode('utf-8')
            error = error.decode('utf-8')

            if error:
                socketio.emit('code_output', {'output': f'Error: {error}', 'error': True}, room=sid)
            else:
                socketio.emit('code_output', {'output': output, 'error': False}, room=sid)

        eventlet.spawn(execute_code, code, sid)
    except Exception as e:
        socketio.emit('code_output', {'output': f'Error: {str(e)}', 'error': True}, room=sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('WebSocket Client Disconnected')
    
if __name__ == '__main__':
    print("Running on http://localhost:5000/")
    socketio.run(app)