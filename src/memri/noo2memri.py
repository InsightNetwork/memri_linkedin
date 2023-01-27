import argparse
import json
import os
from typing import List
from memri.LinkedInGraph import LinkedInGraph


ROOT = os.path.dirname(__file__)


def main(file: str, owner_key: str, database_key: str):
    persons: List["LinkedInGraph.NooPerson"] = []
    links: List["LinkedInGraph.NooLink"] = []

    with open(os.path.join(ROOT, file)) as f:
        sdata = f.read()
        m = json.loads(sdata)

        for i in m["result"][0]["profiles"]:
            persons.append(
                LinkedInGraph.NooPerson(
                    externalId=i["_id"],
                    username=i["data"]["profile"]["username"],
                    fullname=i["data"]["profile"]["fullname"],
                    location=i["data"]["profile"].get("loc"),
                    description=i["data"]["profile"].get("desc"),
                )
            )

        for i in m["result"][0]["edges"]:
            p1 = list(filter(lambda x: x.externalId == i[0], persons))
            p2 = list(filter(lambda x: x.externalId == i[1], persons))

            if p1 and p2:
                links.append(
                    LinkedInGraph.NooLink(
                        p1[0],
                        p2[0],
                        i[2],
                    )
                )

    graph = LinkedInGraph(owner_key=owner_key, database_key=database_key)
    graph.bulk_create(persons=persons, links=links)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON -> memri tool")
    parser.add_argument("-f", "--file", type=str, required=True,
                        help="JSON file name")
    parser.add_argument("--owner_key", type=str, required=True)
    parser.add_argument("--database_key", type=str, required=True)
    args = parser.parse_args()
    main(**args.__dict__)
