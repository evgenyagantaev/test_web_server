import http.server
import ssl
import threading
import time

# HTTP request handler that redirects all requests to HTTPS
class RedirectHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        # Construct the HTTPS URL for redirection
        host = self.headers.get('Host')
        target = f"https://{host}{self.path}"
        self.send_header('Location', target)
        self.end_headers()

# HTTPS request handler that serves the calendar page as the start page
class SimpleHTTPSRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Only serve the calendar for the root path or index.html
        if self.path in ["/", "/index.html"]:
            try:
                # Read the calendar HTML file from disk
                with open("calendar_interactive_en.html", "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(404, f"File not found: {str(e)}")
        else:
            # Return 404 for any other paths
            self.send_error(404, "Not Found")

def run_https_server():
    host = "0.0.0.0"
    port = 443  # Standard HTTPS port; may require administrator privileges
    server = http.server.HTTPServer((host, port), SimpleHTTPSRequestHandler)
    
    # Create an SSL context for TLS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # Load the certificate and key
    context.load_cert_chain(
        certfile="/etc/letsencrypt/live/evgenyagantaev.duckdns.org/fullchain.pem",
        keyfile="/etc/letsencrypt/live/evgenyagantaev.duckdns.org/privkey.pem"
    )
    # Wrap the server socket using the SSL context
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    print(f"HTTPS server started at https://{host}:{port}")
    server.serve_forever()

def run_http_redirect_server():
    host = "0.0.0.0"
    port = 80  # Standard HTTP port; may require administrator privileges
    server = http.server.HTTPServer((host, port), RedirectHTTPRequestHandler)
    
    print(f"HTTP redirect server started at http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    # Run HTTPS and HTTP redirect servers concurrently using threads
    https_thread = threading.Thread(target=run_https_server, daemon=True)
    http_thread = threading.Thread(target=run_http_redirect_server, daemon=True)
    
    https_thread.start()
    http_thread.start()
    
    print("Servers are running. Press Ctrl+C to stop.")
    try:
        # Using sleep to avoid high CPU usage
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServers stopped.") 