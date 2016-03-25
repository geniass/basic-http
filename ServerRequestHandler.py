from pathlib import Path

import HttpResponse


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
        norm_path = Path(str(self.static_dir) + self.request.uri)

        if self.request.uri == "/":
            # redirect / to index.html
            norm_path = self.static_dir / "index.html"
        if not norm_path.match(str(self.static_dir) + "/*"):
            # client tried to access a path outside of static_dir!
            self.response.status_code = 403
            self.response.reason = "Forbidden. Don't even try"
        elif norm_path.is_file():
            # send the file
            self.response.content = norm_path.open(mode='rb').read()
        else:
            self.response.status_code = 404
            self.response.reason = "Not found"

        return self.response

    def handle_head(self):
        self.response = self.handle_get()
        # HEAD should return headers only
        self.response.content_length = len(self.response.content)
        self.response.content = b""
        return self.response

    def handle_post(self):
        self.response.content = bytes(
            "<html><body><p>You sent a POST:</p><br><p>{0}</p></body></html>"
            .format(str(self.request.content, "utf-8")), "utf-8")
        self.response.status_code = 401
        self.response.reason = "Unauthorized"
        return self.response

    def handle_put(self):
        self.response.content = bytes(
            "<html><body><p>You sent a POST:</p><br><p>{0}</p></body></html>"
            .format(str(self.request.content, "utf-8")), "utf-8")
        self.response.status_code = 401
        self.response.reason = "Unauthorized"
        return self.response

    def handle_delete(self):
        self.response.content = bytes(
            "<html><body><p>You tried to delete {0} !</p></body></html>"
            .format(self.request.uri), "utf-8")
        self.response.status_code = 401
        self.response.reason = "Unauthorized"
        return self.response
