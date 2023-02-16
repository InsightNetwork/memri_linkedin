import socketserver
import webbrowser
from enum import Enum
from queue import Queue
from typing import List, Optional

import typer
from loguru import logger
from pymemri.pod.client import PodClient
from pymemri.pod.utils import read_pod_key

from linkedin.cli import get_request_handler

app = typer.Typer()


class TokenCallbackHandler:
    """Nothing more than a server that listens for a callback from Twitter"""

    def __init__(
        self,
        client: PodClient,
        scheme: str = "http",
        host: str = "localhost",
        port: int = 3667,
        callback_path="/oauth",
        scopes: List[str] = [
            "tweet.read",
            "tweet.write",
            "users.read",
            "like.read",
            "like.write",
            "follows.read",
            "offline.access",
        ],
    ):
        self.callback_url = f"{scheme}://{host}:{port}{callback_path}"
        self.client = client

        response = client.get_oauth2_authorization_url(
            "twitter",
            scopes=scopes,
            redirect_uri=self.callback_url,
        )
        self.url = response["authorizeUrl"]
        self.pkce_verifier = response["pkceVerifier"]

        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer(
            (host, port),
            get_request_handler(
                callback_path=callback_path,
                on_callback=self.on_callback,
            ),
        )
        self.token_queue: Queue[str] = Queue(maxsize=1)

    def on_callback(self, authorization_response: str):
        self.token_queue.put(authorization_response)

    def get_token(self) -> str:
        self.server.handle_request()
        token = self.token_queue.get()
        access_token = self.client.oauth2_authorize(
            platform="twitter",
            code=token,
            redirect_uri=self.callback_url,
            pkce_verifier=self.pkce_verifier,
        )
        return access_token

    def get_url(self) -> str:
        return self.url


class PodType(str, Enum):
    """The type of Pod to connect to"""

    local = "local"
    dev = "dev"
    prod = "prod"
    uat = "uat"


POD_ADDRESS = {
    PodType.local: "http://localhost:3030",
    PodType.dev: "https://dev.pod.memri.io",
    PodType.prod: "https://pod.memri.io",
    PodType.uat: "https://uat.backend.memri.io",
}


@app.command()
def simulate_oauth2_flow(
    pod: PodType = PodType.local,
    database_key: Optional[str] = None,
    owner_key: Optional[str] = None,
):
    pod_full_address = POD_ADDRESS[pod]
    if database_key is None:
        database_key = read_pod_key("database_key")
    if owner_key is None:
        owner_key = read_pod_key("owner_key")

    if None in [pod_full_address, database_key, owner_key]:
        raise ValueError("Missing Pod credentials")

    print(f"pod_full_address={pod_full_address}\nowner_key={owner_key}\n")
    client = PodClient(
        url=pod_full_address,
        database_key=database_key,
        owner_key=owner_key,
    )

    token = run_oauth2_flow(client=client)
    logger.info(f"Access token: {token}")


def run_oauth2_flow(client: PodClient):
    handler = TokenCallbackHandler(
        client=client,
        scheme="http",
        host="localhost",
        port=3667,
    )
    url = handler.get_url()
    webbrowser.open(url)
    token = handler.get_token()
    return token


if __name__ == "__main__":
    app()
