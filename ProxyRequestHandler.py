from pathlib import Path

from client import Client
import HttpResponse


class ProxyRequestHandler:

    def __init__(self, request, static_dir="./static"):
        self.request = request
        self.static_dir = Path(static_dir).resolve()
        self.response = HttpResponse.HttpResponse()
        self.response.status_code = 400
        self.response.reason = "Bad request"

    def handle(self):
        method = self.request.method
        if method == "GET" or method == "HEAD" or method == "DELETE":
            return self.handle_get_head_delete()
        elif method == "POST" or method == "PUT":
            return self.handle_post_put()
        return self.response

    def handle_get_head_delete(self):
        input_address = self.request.host + self.request.uri
        print("Input Address: " + input_address)

        print('\n***MAKING REQUEST FOR CLIENT...***\n')
        prox_client = Client(input_address, 80, '', 0)
        self.response = prox_client.request(self.request)

        return self.response

        # norm_path = Path(str(self.static_dir) + self.request.uri)
        #
        # if not norm_path.match(str(self.static_dir) + "/*"):
        #     # client tried to access a path outside of static_dir!
        #     self.response.status_code = 403
        #     self.response.reason = "Forbidden. Don't even try"
        # elif norm_path.is_file():
        #     # send the file
        #     self.response.content = norm_path.open(mode='rb').read()
        #     self.response.status_code = 200
        #     self.response.reason = "OK"
        # else:
        #     self.response.status_code = 404
        #     self.response.reason = "Not found"

    def handle_post_put(self):
        input_address = self.request.host + self.request.uri
        print("Input Address: " + input_address)

        print('\n***MAKING REQUEST FOR CLIENT...***\n')
        prox_client = Client(input_address, 80, '', 0)
        self.response = prox_client.request(self.request)

        return self.response
