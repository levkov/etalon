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
api = Api(app, doc='/doc/', title='Hello', description='Hello API Example')


@app.route('/log')
def index():
    return render_template('index.html')

@api.route('/monitor')
@api.doc(description="Health Check data in JSON")
class Monitor(Resource):
    @api.response(200, 'Success')
    def get(self):
        monitor_data = {"service_status": "OK", "jobs_waiting": str(len(q.jobs)), "jobs_failed": str(len(failed_q))}
        return jsonify(monitor_data) 

@api.route('/hello')
@api.doc(description="Get Yor Name")
class Hello(Resource):
    @api.response(200, 'Success')
    @api.doc(params={'name': {'in': 'formData', 'description': 'Your Name'}})
    def post(self):
        job_submit_time = int(time.time())
        output = {}
        output["name"] = request.form['name']
        output["job_submit_time"] = job_submit_time
        job = q.enqueue(hello, output, result_ttl=86400)
        return jsonify({"job": job.id})

@api.route('/result/<string:job_id>')
@api.doc(params={'job_id': 'Job ID'}, description="Get Job Result")
class Result(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Validation Error')
    def get(self, job_id):
        job = q.fetch_job(job_id)
        try:
            if job.result == None:
                job_status = dict(job.meta)
                job_status["job_status"] = job.status
                return jsonify(job_status)
            else:
                job_result = dict(job.result)
                job_result["job_status"] = job.status
                return jsonify(job_result)
        except:
            return jsonify({"status": "error"}), 404       

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)

