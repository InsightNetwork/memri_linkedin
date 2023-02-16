import http.server
from typing import Callable, Type
from urllib.parse import parse_qs, urlsplit


def get_request_handler(
    on_callback: Callable,
    callback_path: str = "/oauth",
) -> Type[http.server.BaseHTTPRequestHandler]:
    """
    This is a factory function that returns a request handler class.

    The returned class will have a reference to the client and oauth_token_secret
    variables that are passed to this function.

    This is needed because the request handler class is instantiated by the
    TCPServer class, and we need to pass the client and oauth_token_secret
    variables to the request handler class.
    """

    class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            params = urlsplit(self.path)
            if params.path == callback_path:
                captured_value = parse_qs(self.path)
                on_callback(captured_value["code"][0])

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    bytes("Authenticated, succesfully created oauth item", "utf-8")
                )

    return MyHttpRequestHandler
