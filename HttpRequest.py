class HttpRequest:
    def __init__(self):
        self.method = 'GET'
        self.host = ''
        self.url = ''
        self.http_version = '1.0'
        self.connection = 'keep-alive'
        self.user_agent = 'Mozilla/5.0'
        self.accept_lang = 'en-US,en;q=0.8'

    def gen_request(self):
        req_str = "{0} {1} HTTP/{2}\r\nHost: {3}\r\n".format(self.method, self.url, self.http_version, self.host)

        # if self.connection: req_str += "Connection: {0}\r\n".format(self.connection)
        # if self.user_agent: req_str += "User-Agent: {0}\r\n".format(self.user_agent)
        # if self.accept_lang: req_str += "Accept-Language: {0}\r\n".format(self.accept_lang)
        # req_str += "Accept: text/html\r\n"
        # req_str += "Accept-Encoding: gzip, deflate, sdch\r\n"

        return bytes(req_str + '\r\n', 'utf-8')
