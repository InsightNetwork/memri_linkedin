from pymemri.pod.client import PodClient


class MemriGraph:
    def __init__(self, owner_key: str = None, database_key: str = None,
                 create_account: bool = True) -> None:
        self._client = None
        self._owner_key = owner_key
        self._database_key = database_key
        self._create_account = create_account

    def setup_schema(self) -> None:
        pass

    @property
    def client(self) -> PodClient:
        if self._client is None:
            self._client = PodClient(
                owner_key=self._owner_key,
                database_key=self._database_key,
                create_account=self._create_account,
            )

            if self._create_account:
                self.setup_schema()

        return self._client
