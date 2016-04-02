import re
import urllib.parse


class HttpMessage:
    """
    Abstract Base class representing any HTTP message
    """
    def gen_message(self):
        """
        Generate bytearray representation of the HttpMessage
        :return: bytearray HTTP message
        """
        pass


class BadRequestError(Exception):

    def __init__(self):
        super(BadRequestError, self).__init__("Bad request")
        self.code = 400

# regexs used for finding start/status line and extracting its fields
# uses regex/python named groups
request_regex = re.compile(
    u'^(?P<method>[A-Z]+) (?P<uri>.*) (?P<version>HTTP/\d\.\d)')
response_regex = re.compile(
    u'^(?P<version>HTTP/\d\.\d) (?P<code>\d{3}) (?P<reason>.+)')


def parse_message(data):
    """
    Takes a HTTP message and extracts all fields
    :param data: HTTP message (request or response) bytearray
        (eg b'HTTP/1.1 200 OK\r\nContent-Length:4\r\nConnection: keep-alive\r\n\r\nData')
     :return: dict containing 'header' and 'content' fields. 'header' is a dict containing extracted headers
    """
    terminator = b'\r\n\r\n'

    message = {'header': {}, 'content': ''}

    # HTML message format:
    # start_line/status_line
    # header field\r\n
    # header field\r\n
    # ...\r\n
    # \r\n (terminator)
    # content (optional)

    header_end = data.find(terminator)
    if header_end < 0:
        # no end of header
        raise BadRequestError()

    if header_end + len(terminator) < len(data):
        # message has some content
        message['content'] = data[header_end + len(terminator):]

    header = str(data[:header_end], 'utf-8')
    # each header on a new line. Format:     field_name: value
    header_list = header.split('\r\n')

    # look for a start/status line
    # have a look at request_regex and response_regex above for details
    start_line = header_list[0]
    req_match = request_regex.match(start_line)
    res_match = response_regex.match(start_line)
    if req_match:
        # message is a request
        message['header']['method'] = req_match.group('method')

        # This is required because when a client makes a request
        # through a proxy, the requestURL must be a full URL
        # so that the proxy knows what host to use
        parsed_url = urllib.parse.urlsplit(req_match.group('uri'))
        if parsed_url.scheme and not parsed_url.scheme == "http":
            raise BadRequestError()
        # make relative url from parsed_url by leaving out scheme and netloc
        message['header']['uri'] = urllib.parse.urlunsplit(('', '',
                                                            parsed_url.path,
                                                            parsed_url.query,
                                                            parsed_url.fragment))
        if not message['header']['uri']:
            raise BadRequestError()
        message['header']['host'] = parsed_url.netloc

        message['header']['http_version'] = req_match.group('version')
    elif res_match:
        # message is a response
        message['header']['http_version'] = res_match.group('version')
        message['header']['status_code'] = res_match.group('code')
        message['header']['reason'] = res_match.group('reason')
    else:
        # message is badly formed
        raise BadRequestError()

    header_list = [h.split(': ') for h in header_list]
    headers = {h[0].lower(): h[1] for h in header_list if len(h) == 2}
    for k, v in headers.items():
        if k not in message['header']:
            message['header'][k] = v.strip()

    return message
