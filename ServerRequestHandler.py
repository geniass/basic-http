from pathlib import Path
from datetime import datetime, timedelta
import HttpResponse
from BasicAuth import decode_auth_string


class ServerRequestHandler:

    def __init__(self, request, static_dir="./static"):
        self.request = request
        self.static_dir = Path(static_dir).resolve()
        self.response = HttpResponse.HttpResponse()
        self.response.status_code = 400
        self.response.reason = "Bad request"

    def handle(self):
        method = self.request.method
        if method == "GET":
            return self.handle_get()
        elif method == "HEAD":
            return self.handle_head()
        elif method == "POST":
            return self.handle_post()
        elif method == "PUT":
            return self.handle_put()
        elif method == "DELETE":
            return self.handle_delete()
        return self.response

    def handle_get(self):
        print("GET " + self.request.uri)
        norm_path = Path(str(self.static_dir) + self.request.uri)

        if self.request.uri == "/":
            # redirect / to index.html
            # norm_path = self.static_dir / "index.html"
            self.response.status_code = 301
            self.response.reason = "Moved permanently"
            self.response.location = "/index.html"
            self.response.content = bytes(
                '<html><body><a href="/index.html"></a></body></html>', 'utf-8')
            return self.response

        if '/coffee' in self.request.uri:
            self.response.status_code = 418
            self.response.reason = "I'm a teapot"
            self.response.content = (self.static_dir / "teapot.html").open(mode="rb").read()
            return self.response

        if not norm_path.match(str(self.static_dir) + "/*"):
            # client tried to access a path outside of static_dir!
            self.response.status_code = 403
            self.response.reason = "Forbidden"
            self.response.content = (self.static_dir / "403.html").open(mode="rb").read()
        elif norm_path.is_file():
            last_modified = datetime.fromtimestamp(norm_path.stat().st_mtime).replace(microsecond=0)
            if_mod_since = datetime.strptime(self.request.if_mod_since, "%a, %d %b %Y %H:%M:%S GMT") if self.request.if_mod_since else datetime.utcnow()
            if if_mod_since < last_modified:
                # send the file
                self.response.content = norm_path.open(mode='rb').read()
                self.response.status_code = 200
                self.response.reason = "OK"
                self.response.last_mod = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
                print(self.response.last_mod)
            else:
                self.response.status_code = 304
                self.response.reason = "Not modified"
        else:
            self.response.status_code = 404
            self.response.reason = "Not found"
            self.response.content = (self.static_dir / "404.html").open(mode="rb").read()

        return self.response

    def handle_head(self):
        self.response = self.handle_get()
        # HEAD should return headers only
        self.response.content_length = len(self.response.content)
        self.response.content = b""
        return self.response

    def handle_post(self):
        if "/index.html" in self.request.uri:
            if not self.request.authorization:
                self.response.status_code = 401
                self.response.reason = "Unauthorized"
                self.response.www_auth = 'Basic realm="ELEN4017"'
                return self.response

            username, password = decode_auth_string(self.request.authorization)
            print(username,password)
            if username == "ThePunisher" and password == "stayD0wn":
                self.response.content = bytes(
                    "<html><body><p>You authenticated as ThePunsiher. You sent a {0}:</p><br><p>{1}</p></body></html>"
                    .format(self.request.method, str(self.request.content, "utf-8")), "utf-8")
                self.response.status_code = 202
                self.response.reason = "Accepted"
                return self.response
            else:
                self.response.status_code = 403
                self.response.reason = "Forbidden"
                self.response.content = b'''<html><body><h1>You are not authorized to view this page!</h1></body></html>'''
                return self.response

        self.response.content = bytes(
            "<html><body><p>You sent a {0}:</p><br><p>{1}</p></body></html>"
            .format(self.request.method, str(self.request.content, "utf-8")), "utf-8")
        self.response.status_code = 202
        self.response.reason = "Accepted"
        return self.response

    def handle_put(self):
        self.response.content = bytes(
            "<html><body><p>You sent a {0}:</p><br><p>{1}</p></body></html>"
            .format(self.request.method, str(self.request.content, "utf-8")), "utf-8")
        self.response.status_code = 202
        self.response.reason = "Accepted"
        return self.response

    def handle_delete(self):
        self.response.content = bytes(
            "<html><body><p>You tried to delete {0} !</p></body></html>"
            .format(self.request.uri), "utf-8")
        self.response.status_code = 202
        self.response.reason = "Accepted"
        return self.response
