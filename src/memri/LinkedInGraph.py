from typing import List
from memri.MemriGraph import MemriGraph
from memri.schema import LinkedInAccount, LinkedInLink


class LinkedInGraph(MemriGraph):
    def setup_schema(self):
        self.client.add_to_schema(LinkedInAccount)

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "VOUCHES_FOR",
                "sourceType": "LinkedInAccount",
                "targetType": "LinkedInAccount",
            }
        )

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "LI",
                "sourceType": "LinkedInAccount",
                "targetType": "LinkedInAccount",
            }
        )

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "CLAIM",
                "sourceType": "LinkedInAccount",
                "targetType": "LinkedInAccount",
            }
        )

    def create_connections(self, owner: LinkedInAccount, connections: List["LinkedInAccount"]):
        self.client.create_if_external_id_not_exists(owner)

        create_edges: List["LinkedInLink"] = []
        create_items: List["LinkedInAccount"] = []

        for i in connections:
            if not self.client.external_id_exists(i):
                create_items.append(i)
                create_edges.append(LinkedInLink(owner, i, "LI"))

        self.client.bulk_action(create_items=create_items, create_edges=create_edges)

    def bulk_create(
        self,
        accounts: List["LinkedInAccount"],
        links: List["LinkedInLink"],
    ):
        self.client.bulk_action(create_items=accounts, create_edges=links)

    def get_accounts(self) -> List["LinkedInAccount"]:
        return self.client.search({"type": "LinkedInAccount"}, include_edges=False)

    def get_links(self, persons: List["LinkedInAccount"]) -> List["LinkedInLink"]:
        links = []

        for i in persons:
            person_links = self.client.get_edges(i.id)
            for j in person_links:
                links.append(LinkedInLink(
                    i,
                    j["item"],
                    j["name"]
                ))

        return links

    def get_owner(self) -> LinkedInAccount:
        result = self.client.search(
            {
                "isMe": True,
                "type": "LinkedInAccount",
                "deleted": False,
            },
            include_edges=False,
        )

        return result[0] if result else None

    def create_owner(self, owner: LinkedInAccount):
        self.client.create_if_external_id_not_exists(owner)
