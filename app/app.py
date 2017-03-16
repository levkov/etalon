from flask import Flask, request, jsonify, render_template
from flask_restplus import Resource, Api
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
api = Api(app, doc='/doc/')


@app.route('/status')
def index():
    return render_template('index.html')

@app.route('/monitor')
def monitor():
    monitor_data = {"service_status": "OK", "jobs": str(len(q.jobs)), "failed": str(len(failed_q))}
    return jsonify(monitor_data)   

@api.route('/hello/<string:name>')
class Hello(Resource):
    def post(self, name):
        job_submit_time = int(time.time())
        output = {}
        output["name"] = name
        output["job_submit_time"] = job_submit_time
        job = q.enqueue(hello, output, result_ttl=86400)
        return jsonify({"job": job.id})

@api.route('/result/<string:job_id>')
class Result(Resource):
    def get(self, job_id):
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

