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
        self.user_agent = ''
        self.accept_lang = 'en-GB,en;q=0.5'
        self.accept_encoding = 'gzip, deflate'
        self.accept = '/'
        self.content_type = 'application/x-www-form-urlencoded'
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

    def gen_request(self):
        """
        Generates a bytearray request message that can be transmitted
        Uses the data contained in this HttpRequest instance
        :return: Http request message as a bytearray
        """
        if self.method: req_str = self.method + ' '
        if self.uri: req_str += self.uri + ' '
        if self.http_version: req_str += '{0}\r\n'.format(self.http_version)
        if self.host: req_str += 'Host: {0}\r\n'.format(self.host)
        if self.user_agent: req_str += 'User-Agent: {0}\r\n'.format(self.user_agent)

        if (self.method == 'GET') or (self.method == 'HEAD') or (self.method == 'DELETE'):
            pass

        if (self.method == 'POST') or (self.method == 'PUT'):
            req_str += 'Accept: {0}\r\nAccept-Language: {1}\r\nAccept-Encoding: {2}\r\nContent-Type: {3}\r\n' \
                       'Content-Length: {4}\r\nConnection: {5}\r\n\n{6}\n'.format(self.accept, self.accept_lang,
                                                            self.accept_encoding, self.content_type,
                                                            self.content_length, self.connection, self.content)

        return bytes((req_str + '\r\n'), 'ISO-8859-1')
