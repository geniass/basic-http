import HttpRequest


def recv_content(sock_file, content_length):
    """
    Reads content_length bytes from sock_file
    :param sock_file: a file (usually) created by socket.makefile()y
    :param content_length: number of bytes to read from sock_file
    :return: content_length bytes from sock_file
    """
    chunks = bytearray()
    print("content length", content_length)
    while len(chunks) < content_length:
        chunk = sock_file.read(min(content_length - len(chunks), 2048))
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        chunks.extend(chunk)
    return chunks


def recv_header(sock_file):
    """
    Reads a HTTP header from sock_file (upto the \r\n line)
    :param sock_file: a file (usually) created by socket.makefile()
    :return: the HTTP header
    """
    header = bytearray()
    for line in sock_file:
        header.extend(line)
        if line == b"\r\n":
            break
    return header


def recv_message(socket):
    """
    Receives a HTTP message from sock
    :param sock: socket to read from
    :return: HttpRequest object with headers and content (if present)
    """
    with socket.makefile('rb') as sock_file:
        header = recv_header(sock_file)
        request = HttpRequest.HttpRequest(request=header)
        if request.content_length:
            request.content = recv_content(sock_file, request.content_length)
        return request
