def recv_content(sock, content_length):
    """
    Reads content_length bytes from sock
    :param sock: open socket to read from
    :param content_length: number of bytes to read from sock
    :return: content_length bytes from sock
    """
    chunks = bytearray()
    print("content length",content_length)
    print("chunks",len(chunks))
    while len(chunks) < content_length:
        print(len(chunks))
        print("recv", min(content_length - len(chunks), 2048))
        chunk = sock.recv(min(content_length - len(chunks), 2048))
        print("chunk", repr(chunk))
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        chunks.extend(chunk)
    return chunks
