from wsgi import app, initialize_db
from gevent import pywsgi
import os

server = pywsgi.WSGIServer((os.environ.get("WSGI_HOST", "0.0.0.0"), int(os.environ.get("WSGI_PORT", "8060"))), app)
initialize_db()
server.serve_forever()
