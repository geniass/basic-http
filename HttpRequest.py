from HttpMessage import parse_message
from HttpMessage import BadRequestError


class HttpRequest:
    def __init__(self, request=""):
        """
        Creates a HttpRequest with default properties, unless a request message string is provided
        :param request: message string to be parsed
        :return: new HttpRequest
        """
        self.method = 'GET'
        self.host = ''
        self.uri = ''
        self.http_version = '1.0'
        self.connection = 'keep-alive'
        self.user_agent = 'Mozilla/5.0'
        self.accept_lang = 'en-US,en;q=0.8'

        if request:
            message = parse_message(request)
            if message['content']:
                if 'Content-Length' not in message:
                    raise BadRequestError()
                self.content = message['content']

            header = message['header']
            if 'method' in header: self.method = header['method']
            if 'host' in header: self.host = header['host']
            if 'uri' in header: self.uri = header['uri']

    def gen_request(self):
        req_str = "{0} {1} HTTP/{2}\r\nHost: {3}\r\n".format(self.method, self.uri, self.http_version, self.host)

        if self.connection: req_str += "Connection: {0}\r\n".format(self.connection)
        if self.user_agent: req_str += "User-Agent: {0}\r\n".format(self.user_agent)
        if self.accept_lang: req_str += "Accept-Language: {0}\r\n".format(self.accept_lang)

        return bytes(req_str + '\r\n', 'utf-8')
