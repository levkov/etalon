from rq import Queue
from redis import Redis
from rq import get_current_job
import time

redis_conn = Redis()
q = Queue(connection=redis_conn)


def hello(name):
    job = get_current_job()
    job.meta['status'] = "working..."
    job.save()
    time.sleep(60)
    return {"answer": "Hello " + str(name)}
