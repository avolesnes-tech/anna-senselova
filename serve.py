import http.server, os, sys

os.chdir("/Users/annalockwoodova/Documents/test stranka vysivka")
port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
handler = http.server.SimpleHTTPRequestHandler
with http.server.HTTPServer(("", port), handler) as httpd:
    print(f"Serving at http://localhost:{port}")
    httpd.serve_forever()
