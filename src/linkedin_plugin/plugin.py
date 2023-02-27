from memri.LinkedInGraph import LinkedInGraph
from memri.schema import LinkedInAccount
from pymemri.plugin.pluginbase import PluginBase
from pymemri.webserver.public_api import register_endpoint


class LinkedinPlugin(PluginBase):
    schema_classes = [
        LinkedInAccount,
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.graph = LinkedInGraph(client=self.client)
        self.daemon = True

    def run(self):
        pass

    @register_endpoint("/v1/graph", "GET")
    def get_graph(self):
        accounts = self.graph.get_accounts()
        links = self.graph.get_links(accounts)

        data = {
            "nodes": [i.to_json() for i in accounts],
            "links": [{"source": i.source.id, "target": i.target.id, "type": i.name} for i in links],
        }

        return data


if __name__ == '__main__':
    from pymemri.pod.client import PodClient
    from starlette.config import Config
    import os

    ROOT = os.path.dirname(__file__)

    config = Config(os.path.join(ROOT, '.env'))

    OWNER_KEY = config('VIS_OWNER_KEY', cast=str)
    DATABASE_KEY = config('VIS_DATABASE_KEY', cast=str)

    client = PodClient(
        owner_key=OWNER_KEY,
        database_key=DATABASE_KEY,
        create_account=True,
    )

    plugin = LinkedinPlugin(client=client)
    plugin.add_to_schema()
    plugin._run()
