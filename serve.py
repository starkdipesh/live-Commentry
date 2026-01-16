import http.server
import socketserver
import webbrowser
import os
import socket
import json
import asyncio
import threading
from urllib.parse import urlparse
from pathlib import Path

# Try to import edge_tts and other dependencies for audio
try:
    import edge_tts
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    # Define a stub for edge_tts to prevent NameError
    class edge_tts_stub:
        class Communicate:
            def __init__(self, *args, **kwargs): pass
            async def save(self, *args, **kwargs): pass
    edge_tts = edge_tts_stub()
    print("⚠️ Packages missing: pip install edge-tts pygame")

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

PORT = get_free_port()
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

async def speak_text(text):
    """Generate and play speech using edge-tts"""
    if not text: return
    print(f"🎙️ Speaking: {text}")
    try:
        voice = "hi-IN-SwaraNeural"
        temp_file = Path(DIRECTORY) / "temp_speech.mp3"
        communicate = edge_tts.Communicate(text, voice, rate="+15%")
        await communicate.save(str(temp_file))
        
        if PYGAME_AVAILABLE:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(str(temp_file))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
        else:
            # Fallback for Ubuntu if pygame fails
            os.system(f"mpg123 -q '{temp_file}' 2>/dev/null || paplay '{temp_file}' 2>/dev/null")
            
        if temp_file.exists():
            temp_file.unlink()
    except Exception as e:
        print(f"❌ Speak Error: {e}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/speak':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            text = data.get('text', '')
            
            # Run TTS in a new event loop in a separate thread to not block the server
            def run_async_speak():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(speak_text(text))
                loop.close()
            
            threading.Thread(target=run_async_speak).start()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "speaking"}).encode())
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_server():
    # Use ThreadingTCPServer to handle multiple requests if needed
    class ThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        pass

    with ThreadingServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"\n🚀 PARTHASARATHI SECURE GATEWAY LIVE!")
        print(f"🔗 URL: {url}")
        print(f"🛡️ Note: Python-based TTS enabled via '/speak' endpoint.")
        print(f"   (Press Ctrl+C to stop JARVIS)\n")
        
        webbrowser.open(url)
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()

