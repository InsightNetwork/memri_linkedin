from pymemri.plugin.pluginbase import PluginBase
from pymemri.pod.client import PodClient
from pymemri.webserver.public_api import register_endpoint
from memri.schema import LinkedInAccount


class LinkedinPlugin(PluginBase):
    schema_classes = [
        LinkedInAccount,
    ]

    def __init__(self, client: PodClient, *args, **kwargs) -> None:
        super().__init__(*args, client=client, **kwargs)
        self.daemon = True

    def run(self):
        pass


if __name__ == '__main__':
    import os
    from starlette.config import Config
    from memri.LinkedInGraph import LinkedInGraph

    ROOT = os.path.dirname(__file__)

    config = Config(os.path.join(ROOT, '.env'))

    OWNER_KEY = config('VIS_OWNER_KEY', cast=str)
    DATABASE_KEY = config('VIS_DATABASE_KEY', cast=str)

    graph = LinkedInGraph(
        owner_key=OWNER_KEY,
        database_key=DATABASE_KEY,
        create_account=True)

    plugin = LinkedinPlugin(graph.client)

    plugin._run()
