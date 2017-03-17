#!/usr/bin/env python
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from app import *
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(10)
        socketio.emit('my_response',
                      {'data': 'Jobs Waiting: ' 
                      + str(q.count) 
                      + ' | Failed: ' 
                      + str(failed_q.count) 
                      + " | Waiting Job IDs: " 
                      + str(q.job_ids).replace("u\'", "").replace("\'", "")},
                      namespace='/log')

@socketio.on('my_ping', namespace='/log')
def ping_pong():
    emit('my_pong')

@socketio.on('connect', namespace='/log')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
