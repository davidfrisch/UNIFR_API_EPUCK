from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send, join_room
from flask_cors import CORS, cross_origin


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_HEADERS'] = 'Content-Type'
socketio = SocketIO(app, cors_allowed_origins="*")
monitor_socket_id = None

@app.route("/")
def index():
    return render_template('index.html')


@socketio.on('broadcast')
def handle_broadcast(data):
    sender = data['from']
    msg = data['msg']
    emit('broadcast', msg, broadcast=True, include_self=False)
    emit('send_broadcast_to_monitor', {'from': sender, 'msg':msg, 'is_receiver': False}, broadcast=True, include_self=False)


@socketio.on('confirm_reception')
def confirm_reception(data):
    id = data['id']
    msg = data['msg']
    timestamp = data['timestamp']
    emit('confirm_reception_to_monitor', {'id': id, 'msg':msg, 'is_receiver': True, 'timestamp': timestamp}, broadcast=True, include_self=False)


@socketio.on('monitor_online')
def monitor_online(socket_id):
    global monitor_socket_id
    monitor_socket_id = socket_id
    
@socketio.on('new_connection')
def new_connection(data):
    new_robot = data['new_robot']
    print(f"{new_robot} is connect")
    emit('new_robot', {'new_robot':new_robot, 'msg':'joined the party'}, broadcast=True, include_self=False)


@socketio.on('ask_who_is_alive')
def ask_who_is_alive():
    emit('who_is_alive', broadcast=True, include_self=False)

@socketio.on('i_am_alive')
def i_am_alive(data):
    emit('is_alive', data, broadcast=True, include_self=False)

@socketio.on('send_msg_to')
def handle_send_msg_to(data):
    dest = data['dest']
    msg = data['msg']
    # send msg
    emit(dest+'_on_receive', msg, broadcast=True, include_self=False)
    
@socketio.on('stream_img')
def stream_img(data):
    global monitor_socket_id
    id = data['id']
    img = data['img']
    if monitor_socket_id:
        emit(f"{id}_stream_img_monitor", img, room=monitor_socket_id)


@socketio.on('init_camera')
def init_camera(data):
    global monitor_socket_id
    id = data['id']
    print(id+' start camera')
    if monitor_socket_id:
        emit(f"{id}_init_camera", room=monitor_socket_id) 

@socketio.on('disable_camera')
def disable_camera(data):
    global monitor_socket_id
    id = data['id']
    
    if monitor_socket_id:
        emit(f"{id}_disable_camera", room=monitor_socket_id)


def start_flask_server():
    socketio.run(app, debug=False, port=8000)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000)
