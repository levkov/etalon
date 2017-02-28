from rq import Queue
from redis import Redis
from rq import get_current_job
import time

redis_conn = Redis()
q = Queue(connection=redis_conn)


def hello(name):
    i = 60
    while i > 1:
        job = get_current_job()
        job.meta['status'] = "working..." + str(i) + " seconds left"
        job.save()
        i -= 1
        time.sleep(1)
    return {"answer": "Hello " + str(name)}
