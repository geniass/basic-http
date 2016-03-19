from HttpMessage import parse_message
from HttpMessage import BadRequestError


class HttpRequest:
    def __init__(self, request=""):
        """
        Creates a HttpRequest with default properties, unless a request message is provided
        :param request: (optional) message bytearray to be parsed
            (eg. 'GET /more HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nConnection: keep-alive\r\n\r\n')
        :return: new HttpRequest
        """

        # construct default request object
        self.method = 'GET'
        self.host = ''
        self.uri = ''
        self.http_version = 'HTTP/1.0'
        self.connection = 'keep-alive'
        self.user_agent = 'Mozilla/5.0'
        self.accept_lang = 'en-US,en;q=0.8'

        if request:
            # request bytearray was provided. Need to parse it
            message = parse_message(request)
            if message['content']:
                if 'Content-Length' not in message:
                    # content was sent, but no Content-Length specified
                    raise BadRequestError()
                self.content = message['content']

            # check if the relevant header fields are present in the message
            # TODO: add more header fields eg User-Agent
            header = message['header']
            if 'method' in header: self.method = header['method']
            if 'host' in header: self.host = header['host']
            if 'uri' in header: self.uri = header['uri']
            if 'http_version' in header: self.http_version = header['http_version']

    def gen_request(self):
        """
        Generates a bytearray request message that can be transmitted
        Uses the data contained in this HttpRequest instance
        :return: Http request message as a bytearray
        """
        req_str = "{0} {1} {2}\r\n".format(self.method, self.uri, self.http_version)

        # TODO: add more fields such as Accepts and content
        if self.host: req_str += "Host: {0}\r\n".format(self.host)
        if self.connection: req_str += "Connection: {0}\r\n".format(self.connection)
        if self.user_agent: req_str += "User-Agent: {0}\r\n".format(self.user_agent)
        if self.accept_lang: req_str += "Accept-Language: {0}\r\n".format(self.accept_lang)

        return bytes(req_str + '\r\n', 'utf-8')
