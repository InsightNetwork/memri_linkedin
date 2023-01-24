from pymemri.data.schema import Edge
from pymemri.data.schema.itembase import ItemBase
from typing import List, Optional
from MemriGraph import MemriGraph


class LinkedInGraph(MemriGraph):
    class Person(ItemBase):
        username: Optional[str] = None
        fullname: Optional[str] = None
        location: Optional[str] = None
        description: Optional[str] = None

    class Link(Edge):
        pass

    def setup_schema(self):
        self.client.add_to_schema(LinkedInGraph.Person)

        self.client.api.create_item(
            {
                "type": "ItemEdgeSchema",
                "edgeName": "link",
                "sourceType": "LinkedInGraph.Person",
                "targetType": "LinkedInGraph.Person",
            }
        )

    def bulk_create(
        self,
        persons: List["LinkedInGraph.Person"],
        links: List["LinkedInGraph.Link"],
    ):
        self.client.bulk_action(create_items=persons, create_edges=links)
