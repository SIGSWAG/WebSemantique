from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "localhost"
hostPort = 9000

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.path is '/':
            self.wfile.write(bytes("<html><head><title>Title goes here.</title></head></html>", "utf-8"))

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), ":: Server Starting")

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), ":: Server Stoped")