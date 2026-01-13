import http.server
import socketserver
import webbrowser
import os
import socket

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

PORT = get_free_port()
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"\n🚀 PARTHASARATHI SECURE GATEWAY LIVE!")
        print(f"🔗 URL: {url}")
        print(f"🛡️ Note: Accessing via 'localhost' unlocks Mic and Screen Share.")
        print(f"   (Press Ctrl+C to stop JARVIS)\n")
        
        # Automatically open the browser
        webbrowser.open(url)
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()
