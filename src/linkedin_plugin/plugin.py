from pymemri.plugin.pluginbase import PluginBase
from pymemri.pod.client import PodClient
from pymemri.webserver.public_api import register_endpoint
from linkedin_plugin.schema import Account


class LinkedinPlugin(PluginBase):
    def __init__(self, client: PodClient, *args, **kwargs) -> None:
        super().__init__(*args, client=client, **kwargs)

    def add_to_schema(self):
        return self.client.add_to_schema(
            Account,
        )

    def run(self):
        pass
