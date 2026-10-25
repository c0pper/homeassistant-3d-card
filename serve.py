#!/usr/bin/env python3
"""Tiny static server with CORS for previewing the floor3d model."""

import http.server
import os
import socketserver

PORT = 8765
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"serving {ROOT} on http://0.0.0.0:{PORT}", flush=True)
    httpd.serve_forever()
