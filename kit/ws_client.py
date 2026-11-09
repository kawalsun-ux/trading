"""Minimal WebSocket client (stdlib only)."""
import socket, ssl, base64, hashlib, struct, time

def connect(url, timeout=10):
    # url: ws://host:port/path or wss://host:port/path
    import urllib.parse
    u = urllib.parse.urlsplit(url)
    host = u.hostname
    port = u.port or (443 if u.scheme == "wss" else 80)
    path = u.path or "/"
    if u.query:
        path += "?" + u.query
    sock = socket.create_connection((host, port), timeout=timeout)
    if u.scheme == "wss":
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(sock, server_hostname=host)
    key = base64.b64encode(os.urandom(16) if False else __import__("os").urandom(16)).decode()
    req = (f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\n"
           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
    sock.sendall(req.encode())
    # read handshake
    data = b""
    while b"\r\n\r\n" not in data:
        c = sock.recv(4096)
        if not c:
            raise ConnectionError("handshake failed")
        data += c
    return sock, key

def send_text(sock, text):
    from rfc import websocket as ws
    sock.sendall(ws.encode_text(text, mask=True))

def recv_frame(sock, timeout=None):
    if timeout is not None:
        sock.settimeout(timeout)
    buf = b""
    while len(buf) < 2:
        c = sock.recv(2 - len(buf))
        if not c:
            return None
        buf += c
    b0, b1 = buf[0], buf[1]
    fin = bool(b0 & 0x80)
    opcode = b0 & 0x0F
    masked = bool(b1 & 0x80)
    length = b1 & 0x7F
    if length == 126:
        while len(buf) < 4:
            buf += sock.recv(4 - len(buf))
        length = struct.unpack("!H", buf[2:4])[0]
        idx = 4
    elif length == 127:
        while len(buf) < 10:
            buf += sock.recv(10 - len(buf))
        length = struct.unpack("!Q", buf[2:10])[0]
        idx = 10
    else:
        idx = 2
    if masked:
        while len(buf) < idx + 4:
            buf += sock.recv(idx + 4 - len(buf))
        key = buf[idx:idx+4]
        idx += 4
    while len(buf) < idx + length:
        buf += sock.recv(idx + length - len(buf))
    payload = buf[idx:idx+length]
    if masked:
        payload = bytes(payload[i] ^ key[i % 4] for i in range(len(payload)))
    return opcode, payload, fin