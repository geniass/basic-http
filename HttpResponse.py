from datetime import datetime

from HttpMessage import parse_message
from HttpMessage import HttpMessage


class HttpResponse(HttpMessage):

    def __init__(self, response=""):
        """
        Creates a HttpResponse with default properties,
        unless a response message is provided
        :param response: (optional) message bytearray to be parsed
        :return: new HttpResponse
        """

        # construct default response object
        self.http_version = 'HTTP/1.0'
        self.status_code = 200
        self.reason = "OK"
        self.connection = 'keep-alive'
        self.date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.location = ""
        self.content_length = 0
        self.content = b""

        if response:
            # response bytearray was provided. Need to parse it
            message = parse_message(response)
            if message['content']:
                if 'content-length' not in message:
                    # raise BadRequestError()
                    # TODO: BadResponse
                    pass
                self.content = message['content']

            # check if the relevant header fields are present in the message
            # TODO: add more header fields eg User-Agent
            header = message['header']
            if 'http_version' in header:
                self.http_version = header['http_version']
            if 'status_code' in header:
                self.status_code = int(header['status_code'])
            if 'reason' in header:
                self.reason = header['reason']
            if 'content-length' in header:
                self.content_length = int(header['content-length'])
            if 'connection' in header:
                self.connection = header['connection']
            if 'date' in header:
                self.date = header['date']
            if 'location' in header:
                self.location = header['location']
            if 'last-modified' in header:
                self.last_mod = header['last-modified']

    def gen_message(self):
        """
        Generates a bytearray response message that can be transmitted
        Uses the data contained in this HttpResponse instance
        :return: Http response message as a bytearray
        """
        req_str = "{0} {1} {2}\r\n".format(
            self.http_version, self.status_code, self.reason)
        req_str += "Date: {0}\r\n".format(self.date)

        # TODO: add more fields such as Accepts and content
        if self.connection:
            req_str += "Connection: {0}\r\n".format(self.connection)
        if self.location:
            req_str += "Location: {0}\r\n".format(self.location)

        if self.content_length:
            req_str += "Content-Length: {0}\r\n".format(self.content_length)
        elif self.content:
            req_str += "Content-Length: {0}\r\n".format(len(self.content))

        req_str += "\r\n"
        req_bytes = bytearray(req_str, 'utf-8')
        if self.content:
            req_bytes.extend(self.content)

        return req_bytes
