
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import subprocess
import shutil
import sys
import os
import getpass
import time
print("Notice: When running, press ^C (Ctrl+C) to stop. May need to press twice on ngrok.")
HOST = "127.0.0.1"
PORT = 8000
NGROK_DOMAIN = "deduct-moocher-gulf.ngrok-free.dev"
BASE_DIR = Path(__file__).resolve().parent
DIRECTORY = BASE_DIR / "dashboard"
handler = partial(
    SimpleHTTPRequestHandler,
    directory=str(DIRECTORY)
)
server = HTTPServer((HOST, PORT), handler)
tunnel = None
try:
    ngrok = shutil.which("ngrok")
    if not ngrok:
        raise FileNotFoundError("ngrok is not installed")
    check = subprocess.run(
        [ngrok, "config", "check"],
        capture_output=True,
        text=True
    )
    if check.returncode != 0:
        print("\n! Warn: ngrok authentication required !")
        token = getpass.getpass("Enter your ngrok authtoken: ").strip()
        if not token:
            raise ValueError("No ngrok token provided")
        subprocess.run(
            [ngrok, "config", "add-authtoken", token],
            check=True
        )
        print("ngrok authenticated successfully.")
    tunnel = subprocess.Popen([
        ngrok,
        "http",
        f"--url=https://{NGROK_DOMAIN}",
        str(PORT)
    ])
    print(f"Public URL: https://{NGROK_DOMAIN}")
except (FileNotFoundError, ValueError, subprocess.CalledProcessError, OSError) as e:
    print(f"\n!!! Tunnel error: {e} !!!")
    print("Running without ngrok.")
print(f"Server running at http://{HOST}:{PORT}")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\Halting...")
finally:
    server.server_close()
    if tunnel and tunnel.poll() is None:
        tunnel.terminate()
        try:
            tunnel.wait(timeout=5)
        except subprocess.TimeoutExpired:
            tunnel.kill()
            tunnel.wait()
    print("Halted.")