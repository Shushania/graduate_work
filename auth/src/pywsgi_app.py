from gevent import monkey, pywsgi

monkey.patch_all()

from src.app import app, main

http_server = pywsgi.WSGIServer(("", 5000), main(app))
http_server.serve_forever()