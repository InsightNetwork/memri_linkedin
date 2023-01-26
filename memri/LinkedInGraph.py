from pymemri.data.schema import Edge, Item
from typing import List, Optional
from MemriGraph import MemriGraph


class LinkedInGraph(MemriGraph):
    class NooPerson(Item):
        username: str
        fullname: str
        location: Optional[str] = None
        description: Optional[str] = None

    class NooLink(Edge):
        pass

    def setup_schema(self):
        self.client.add_to_schema(LinkedInGraph.NooPerson)

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "VOUCHES_FOR",
                "sourceType": "NooPerson",
                "targetType": "NooPerson",
            }
        )

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "LI",
                "sourceType": "NooPerson",
                "targetType": "NooPerson",
            }
        )

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "CLAIM",
                "sourceType": "NooPerson",
                "targetType": "NooPerson",
            }
        )

    def bulk_create(
        self,
        persons: List["LinkedInGraph.NooPerson"],
        links: List["LinkedInGraph.NooLink"],
    ):
        self.client.bulk_action(create_items=persons, create_edges=links)

    def get_persons(self) -> List["LinkedInGraph.NooPerson"]:
        return self.client.search({"type": "NooPerson"}, include_edges=False)

    def get_links(self, persons: List["LinkedInGraph.NooPerson"]
                  ) -> List["LinkedInGraph.NooLink"]:
        links = []

        for i in persons:
            person_links = self.client.get_edges(i.id)
            for j in person_links:
                links.append(LinkedInGraph.NooLink(
                    i,
                    j["item"],
                    j["name"]
                ))

        return links
