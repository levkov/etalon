from rq import Queue
from redis import Redis
from rq import get_current_job
import time

redis_conn = Redis()
q = Queue(connection=redis_conn)


def hello(inpt):
    start_time = int(time.time())
    i = 60
    while i > 1:
        job = get_current_job()
        job.meta['message'] = "working..." + str(i) + " seconds left"
        job.meta["update_timestamp"] = str(int(time.time()))
        job.save()
        i -= 1
        time.sleep(1)
#        i = i/0   #test failure
    stop_time = int(time.time())
    run_time = str(stop_time - start_time)
    wait_time = str(start_time - int(inpt["job_submit_time"]))
    job_timestamp = str(start_time)
    return {"answer": "Hello " + str(inpt["name"]), 
            "job_info": {"job_run_time": run_time, 
            "job_wait_time": wait_time,
            "job_start_time": job_timestamp, 
            "job_submit_time": str(inpt["job_submit_time"])}}
