import multiprocessing
import gevent.monkey
from settings import BASE_DIR, join

gevent.monkey.patch_all()
GUNICORN_LOG_PATH = join(BASE_DIR, 'gunicorn_log')

debug = True
loglevel = 'debug'
bind = '127.0.0.1:5000'
pidfile = join(GUNICORN_LOG_PATH, 'gunicorn.pid')
logfile = join(GUNICORN_LOG_PATH, 'debug.log')

workers = multiprocessing.cpu_count() * 2
threads = 2
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

x_forwarded_for_header = 'X-FORWARDED_FOR'
