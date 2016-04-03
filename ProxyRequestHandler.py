from pathlib import Path
from datetime import datetime, timedelta
from client import Client
import HttpResponse
import caching
import dataset


class ProxyRequestHandler:

    def __init__(self, request, port=8000, static_dir="./static"):
        self.request = request
        self.port = port
        self.static_dir = Path(static_dir).resolve()
        self.response = HttpResponse.HttpResponse()
        self.response.status_code = 400
        self.response.reason = "Bad request"

    def handle(self):
        method = self.request.method
        if method == "GET" or method == "HEAD":
            return self.handle_get_head()
        elif method == "POST" or method == "PUT" or method == "DELETE":
            return self.handle_post_put_delete()
        return self.response

    def handle_get_head(self):
        db = dataset.connect('sqlite:///cache.db')
        cache = db['user']

        request_key = self.request.method + " " + self.request.uri + " " + self.request.http_version + \
                      "\nHost: " + self.request.host

        request_status = caching.check_if_cache_fresh(request_key,cache)

        # If not in cache, or object in cache is outdated, make request again
        if request_status['status'] == 'Request not found in cache' or \
                        request_status['status'] == 'Outdated cache entry. Requesting again':

            print(request_status['status'] + '\n\n')
            input_address = self.request.host + self.request.uri

            print('***MAKING REQUEST FOR CLIENT...***\n')
            prox_client = Client(input_address, self.port, '', 0)
            self.response = prox_client.request(self.request)

            # Made request again, now save in cache, IF cache-able
            caching.save_in_cache(request_key, self.response, cache)

            return self.response

        elif request_status['status'] == "Found in cache. But no expiry or max-age. Make conditional get request":
            print(request_status['status'] + '\n\n')

            # Make request again with if-modified-since header
            input_address = self.request.host + self.request.uri

            self.request.if_mod_since = request_status['last_mod']
            self.request.if_mod_since = datetime.strftime(self.request.if_mod_since, "%a, %d %b %Y %H:%M:%S GMT")
            print('***MAKING CONDITIONAL GET...***\n')
            prox_client = Client(input_address, self.port, '', 0)
            self.response = prox_client.request(self.request)

            # Check modification status
            # If server says it hasn't been modified, return page in cache with "Not Modified" status
            if self.response.status_code == 304:
                self.response = HttpResponse.HttpResponse(request_status['page'])
            # Else it has been modified, save the new response in the cache, if cache-able
            else:
                caching.save_in_cache(request_key, self.response, cache)

            return self.response

        else:
            # It was found in the cache, and is fresh. Return this cached page
            print(request_status['status'] + '\n\n')
            self.response = HttpResponse.HttpResponse(request_status['page'])
            # If the client manually made an if-mod-since request, let client know it's not modified
            if self.request.if_mod_since:
                self.response.status_code = 304
                self.response.reason = "Not Modified"
            return self.response

    def handle_post_put_delete(self):
        print("Please note: The "+self.request.method+" method does not allow caching")
        input_address = self.request.host + self.request.uri

        print('***MAKING REQUEST FOR CLIENT...***\n')
        prox_client = Client(input_address, self.port, '', 0)
        self.response = prox_client.request(self.request)

        return self.response
