import http.server
import socketserver
import os

def find_free_port(address, port):
    Handler = http.server.SimpleHTTPRequestHandler
    for i in range(port, 9000):
        try:
            httpd = socketserver.TCPServer((address, port), Handler)
            return port
        except socketserver.socket.error as exc:
            if exc.args[0] != 48:
                raise
            port += 1
    raise socketserver.socket.error

def load_text(path):
    texts = []
    for i, filename in enumerate(os.listdir(path)):
        if ((filename.endswith('.txt')
             or filename.endswith('.html'))
                 and not filename == 'description.txt'):
            with open(path + filename) as txtfile:
                title = txtfile.readline()
                texts.append({'idname': 'txt%s%i' % (title, i),
                           'title': title,
                           'graph': '<h3>' + title + '</h3><br><pre>' + txtfile.read() + '</pre>'})
    return texts
