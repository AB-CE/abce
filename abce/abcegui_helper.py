import SimpleHTTPServer
import SocketServer


def find_free_port(address, port):
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    for i in range(port, 9000):
        try:
            httpd = SocketServer.TCPServer((address, port), Handler)
            return port
        except SocketServer.socket.error as exc:
            if exc.args[0] != 48:
                raise
            port += 1
    raise SocketServer.socket.error
