import HttpRequest
import HttpResponse


def recv_content(sock_file, content_length=-1):
    """
    Reads content_length bytes from sock_file
    :param sock_file: a file (usually) created by socket.makefile()y
    :param content_length: number of bytes to read from sock_file
    :return: content_length bytes from sock_file
    """
    print("Testing: Content length: ", content_length)
    content = sock_file.read(content_length)
    return content


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


def recv_message(socket, HttpMessageClass=HttpRequest.HttpRequest):
    """
    Receives a HTTP message from sock
    :param sock: socket to read from
    :param HttpMessageClass: the class of the type of message to receive
    (HttpRequest or HttpResponse)
    :return: HttpMessageClass object with headers and content (if present)
    """
    with socket.makefile('rb') as sock_file:
        header = recv_header(sock_file)
        message = HttpMessageClass(header)
        if message.content_length > 0:
            message.content = recv_content(sock_file, message.content_length)
            message.content_length = len(message.content)
        elif message.connection.lower() == "close":
            # www.w3.org/Protocols/HTTP/1.0/spec.html#BodyLength
            # if no content-length specified, then the server must close
            # the connection when finished transmitting
            message.content = recv_content(sock_file)
            message.content_length = len(message.content)
        print("Actual content length: ", len(message.content))
        return message


def recv_response(socket):
    return recv_message(socket, HttpMessageClass=HttpResponse.HttpResponse)


def recv_request(socket):
    return recv_message(socket, HttpMessageClass=HttpRequest.HttpRequest)
