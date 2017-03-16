from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from rq import Queue
from redis import Redis
import time
from common import *

redis_conn = Redis()
q = Queue(connection=redis_conn)
failed_q = Queue('failed', connection=redis_conn)

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

@app.route('/status')
def index():
    return render_template('index.html')


@app.route('/monitor')
def monitor():
    monitor_data = {"jobs": str(len(q.jobs)), "failed": str(len(failed_q))}
    return jsonify(monitor_data)   

@app.route('/hello', methods=['POST'])
def sus():
    job_submit_time = int(time.time())
    output = {}
    output["name"] = request.form["name"]
    output["job_submit_time"] = job_submit_time
    job = q.enqueue(hello, output, result_ttl=86400)
    return jsonify({"job": job.id})

@app.route('/result/<job_id>', methods=['GET'])
def get_job(job_id):
    job = q.fetch_job(job_id)
    try:
        if job.result == None:
            return jsonify(job.meta)
        else:
            return jsonify(job.result)
    except:
        return jsonify({"status": "error"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)

