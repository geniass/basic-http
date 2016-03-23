from HttpMessage import parse_message
from HttpMessage import BadRequestError


class HttpRequest:

    def __init__(self, request=''):
        """
        Creates a HttpRequest with default properties, unless a request message string is provided
        :param request: message string to be parsed
        :return: new HttpRequest
        """
        self.method = 'GET'
        self.host = ''
        self.uri = ''
        self.http_version = 'HTTP/1.1'
        self.connection = 'keep-alive'
        self.user_agent = 'Mozilla/5.0'
        self.accept_lang = 'en-GB,en;q=0.5'
        self.accept_encoding = 'gzip, deflate'
        self.accept = '/'
        self.content_type = 'application/x-www-form-urlencoded'
        # Use content_type = 'multipart/form-data' for file uploads
        self.request = '%40type=issue%26%40action=show%26%40number=12345'
        self.content_length = len(self.request)

        if request:
            message = parse_message(request)
            if message['content']:
                if 'Content-Length' not in message:
                    raise BadRequestError()
                self.content = message['content']

            # check if the relevant header fields are present in the message
            # TODO: add more header fields eg User-Agent
            # Done
            header = message['header']
            if 'method' in header:
                self.method = header['method']
            if 'host' in header:
                self.host = header['host']
            if 'uri' in header:
                self.uri = header['uri']
            if 'http_version' in header:
                self.http_version = header['http_version']
            if 'connection' in header:
                self.connection = header['connection']
            if 'user_agent' in header:
                self.user_agent = header['user_agent']
            if 'accept_lang' in header:
                self.accept_lang = header['accept-lang']
            if 'accept-encoding' in header:
                self.accept_encoding = header['accept-encoding']

    def gen_request(self):
        """
        Generates a bytearray request message that can be transmitted
        Uses the data contained in this HttpRequest instance
        :return: Http request message as a bytearray
        """
        # req_str = "{0} {1} {2}\r\n".format(self.method, self.uri, self.http_version)

        # req_str = "{0} {1} HTTP/{2}\r\nHost: {3}\r\n".format(self.method, self.url, self.http_version, self.host)

        if (self.method == 'GET') or (self.method == 'HEAD') or (self.method == 'DELETE'):
            req_str = "{0} {1} {2}\r\nHost: {3}\r\nUser-Agent: {4}\r\n".format(self.method, self.uri,
                                                                               self.http_version, self.host,
                                                                               self.user_agent)

        elif (self.method == 'POST') or (self.method == 'PUT'):
            req_str = "{0} {1} {2}\r\nHost: {3}\r\nUser-Agent: {4}\r\nAccept: {5}\r\n," \
                      "Accept-Language: {6}\r\nAccept-Encoding: {7}\r\nContent-Type: {8}\r\nContent-Length: {9}\r\n," \
                      "Connection: {10}\r\n\n{10}\n".format(self.method, self.uri, self.http_version, self.host,
                                                            self.user_agent, self.accept, self.accept_lang,
                                                            self.accept_encoding, self.content_type,
                                                            self.content_length, self.connection, self.request)

        # I've completed them but I commented them out and went back to the old format because they keep causing
        # bad requests and I can't tell why

        # print('TESTING BEGINNING OF THIS')
        # if self.host: req_str += "Host: {0}\r\n".format(self.host)
        # if self.user_agent: req_str += "User-Agent: {0}".format(self.user_agent)
        # if self.accept_lang: req_str += "Accept-Language: {0}\r\n".format(self.accept_lang)
        # if self.accept_encoding: req_str += "Accept-Encoding: {0}\r\n".format(self.accept_encoding)
        # if self.content_type: req_str += "Content-Type: {0}\r\n".format(self.content_type)
        # if self.content_length: req_str += "Content-Length: {0}\r\n".format(self.content_length)
        # if self.connection: req_str += "Connection: {0}\r\n\n".format(self.connection)
        # print('TESTING END OF THIS')

        return bytes(req_str + '\r\n', 'utf-8')
