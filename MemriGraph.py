from pymemri.pod.client import PodClient


class MemriGraph:
    def __init__(self) -> None:
        self._client = None

    def setup_schema(self):
        pass

    @property
    def client(self) -> PodClient:
        if self._client is None:
            self._client = PodClient()
            self.setup_schema()
        return self._client
