from pathlib import Path

from client import Client
import HttpResponse
import caching
import dataset


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
        db = dataset.connect('sqlite:///cache.db')
        cache = db['user']

        request_status = caching.check_if_cache_fresh(self.request.gen_message(), cache)

        # If not in cache, or object in cache is outdated, make request again
        if request_status == 'Request not found in cache' or \
                        request_status == 'Outdated cache entry. Requesting again':

            print(request_status + '\n\n')

            input_address = self.request.host + self.request.uri
            print("Input Address: " + input_address)

            print('\n***MAKING REQUEST FOR CLIENT...***\n')
            prox_client = Client(input_address, 80, '', 0)
            self.response = prox_client.request(self.request)

            # Made request again, now save in cache, IF cache-able
            caching.save_in_cache(self.request.gen_message(), self.response, cache)

            return self.response

        else:
            self.response = HttpResponse.HttpResponse(request_status)
            return self.response


    def handle_post_put(self):
        print("Please note: The "+self.request.method+" method does not allow caching")
        input_address = self.request.host + self.request.uri
        # print("Input Address: " + input_address)

        print('\n***MAKING REQUEST FOR CLIENT...***\n')
        prox_client = Client(input_address, 80, '', 0)
        self.response = prox_client.request(self.request)

        return self.response
