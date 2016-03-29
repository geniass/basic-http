from HttpMessage import parse_message
from HttpMessage import BadRequestError
from HttpMessage import HttpMessage


class HttpRequest(HttpMessage):

    def __init__(self, request=''):
        """
        Creates a HttpRequest with default properties, unless a request message string is provided
        :param request: message string to be parsed
        :return: new HttpRequest
        """
        self.method = 'GET'
        self.host = ''
        self.uri = '/'
        self.http_version = 'HTTP/1.0'
        self.connection = 'keep-alive'
        self.user_agent = 'curl/7.40.0'
        self.accept_lang = 'en-GB,en;q=0.5'
        self.accept_encoding = ''
        self.accept = '*/*'
        self.content_type = 'raw'
        # Use content_type = 'multipart/form-data' for file uploads
        self.content = b''
        self.content_length = len(self.content)

        if request:
            message = parse_message(request)
            if message['content']:
                if 'content-length' not in message:
                    raise BadRequestError()
                self.content = message['content']

            # check if the relevant header fields are present in the message
            header = message['header']
            if 'method' in header:
                self.method = header['method']
            if 'host' in header:
                self.host = header['host']
            if 'uri' in header:
                self.uri = header['uri']
            if 'http_version' in header:
                self.http_version = header['http_version']
            if 'content-length' in header:
                self.content_length = int(header['content-length'])
            if 'connection' in header:
                self.connection = header['connection']
            if 'user_agent' in header:
                self.user_agent = header['user_agent']
            if 'accept_lang' in header:
                self.accept_lang = header['accept-lang']
            if 'accept-encoding' in header:
                self.accept_encoding = header['accept-encoding']

    def gen_message(self):
        """
        Generates a bytearray request message that can be transmitted
        Uses the data contained in this HttpRequest instance
        :return: Http request message as a bytearray
        """
        if self.method:
            req_str = self.method + ' '
        if self.uri:
            req_str += self.uri + ' '
        if self.http_version:
            req_str += '{0}\r\n'.format(self.http_version)
        if self.host:
            req_str += 'Host: {0}\r\n'.format(self.host)
        if self.user_agent:
            req_str += 'User-Agent: {0}\r\n'.format(self.user_agent)
        if self.accept:
            req_str += 'Accept: {0}\r\n'.format(self.accept)
        if self.accept_lang:
            req_str += 'Accept-Lang: {0}\r\n'.format(self.accept_lang)
        if self.accept_encoding:
            req_str += 'Accept-Encoding: {0}\r\n'.format(self.accept_encoding)
        if self.connection:
            req_str += 'Connection: {0}\r\n'.format(self.connection)

        if (self.method == 'POST') or (self.method == 'PUT'):
            self.content_length = len(self.content)
            req_str += "Content-Type: {0}\r\nContent-Length: {1}\r\n".format(self.content_type, self.content_length)

            print(req_str)

        req_bytes = bytearray(req_str + "\r\n", "utf-8")
        req_bytes += self.content if self.content else b""
        return req_bytes
