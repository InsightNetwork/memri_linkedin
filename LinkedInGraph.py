from pymemri.data.schema import Edge, Item
from typing import List, Optional
from MemriGraph import MemriGraph


class LinkedInGraph(MemriGraph):
    class Person(Item):
        username: str
        fullname: str
        location: Optional[str] = None
        description: Optional[str] = None

    class Link(Edge):
        pass

    def setup_schema(self):
        self.client.add_to_schema(LinkedInGraph.Person)

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "VOUCHES_FOR",
                "sourceType": "Person",
                "targetType": "Person",
            }
        )

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "LI",
                "sourceType": "Person",
                "targetType": "Person",
            }
        )

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "CLAIM",
                "sourceType": "Person",
                "targetType": "Person",
            }
        )

    def bulk_create(
        self,
        persons: List["LinkedInGraph.Person"],
        links: List["LinkedInGraph.Link"],
    ):
        self.client.bulk_action(create_items=persons, create_edges=links)

    def get_persons(self) -> List["LinkedInGraph.Person"]:
        return self.client.search({"type": "Person"}, include_edges=False)

    def get_links(self, persons: List["LinkedInGraph.Person"]
                  ) -> List["LinkedInGraph.Link"]:
        links = []

        for i in persons:
            person_links = self.client.get_edges(i.id)
            for j in person_links:
                links.append(LinkedInGraph.Link(
                    i,
                    j["item"],
                    j["name"]
                ))

        return links
