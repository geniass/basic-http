from base64 import b64encode
from base64 import b64decode


def encode_auth_string(username, password):
    return str(b64encode(bytes(username + ":" + password, "utf-8")), "utf-8")


def decode_auth_string(auth_string):
    decoded = str(b64decode(bytes(auth_string, "utf-8")), "utf-8")
    parts = decoded.split(":")
    return parts[0], ":".join(parts[1:])