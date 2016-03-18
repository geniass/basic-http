class BadRequestError(Exception):
    def __init__(self):
        super(BadRequestError, self).__init__("Bad request")
        self.code = 400


def parse_message(data):
    terminator = b'\r\n\r\n'

    message = {'header': {}, 'content': ''}

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
    # header_list = [h.split(':') for h in header.split('\n')]

    start_line = header_list[0]
    fields = start_line.split(' ')
    if len(fields) < 3:
        # HTTP response requires at least: version, status code, status reason
        # Request requires method, uri, version
        raise BadRequestError()
    if fields[0].startswith('HTTP'):
        # response message
        message['header']['http_version'] = fields[0]
        message['header']['status_code'] = fields[1]
        message['header']['reason'] = ' '.join(fields[2:])
    else:
        message['header']['method'] = fields[0]
        message['header']['uri'] = fields[1]
        message['header']['http_version'] = fields[2]

    header_list = [h.split(':') for h in header_list]
    headers = {h[0]: h[1] for h in header_list if len(h) == 2}
    for k,v in headers.items():
        if k not in message['header']:
            message['header'][k] = v.strip()

    print(message)
    return message