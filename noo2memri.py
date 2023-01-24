import argparse
import json
from typing import List
from LinkedInGraph import LinkedInGraph


def main(file: str):
    persons: List["LinkedInGraph.Person"] = []
    links: List["LinkedInGraph.Link"] = []

    with open(file) as f:
        sdata = f.read()
        m = json.loads(sdata)

        for i in m["result"][0]["profiles"]:
            persons.append(
                LinkedInGraph.Person(
                    key=i["_id"],
                    username=i["data"]["profile"]["username"],
                    fullname=i["data"]["profile"]["fullname"],
                    location=i["data"]["profile"].get("loc"),
                    description=i["data"]["profile"].get("desc"),
                )
            )

        for i in m["result"][0]["edges"]:
            p1 = list(filter(lambda x: x.key == i[0], persons))
            p2 = list(filter(lambda x: x.key == i[1], persons))

            if p1 and p2:
                links.append(
                    LinkedInGraph.Link(
                        p1[0],
                        p2[0],
                        i[2],
                    )
                )

    graph = LinkedInGraph()
    graph.bulk_create(persons=persons, links=links)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON -> memri tool")
    parser.add_argument("-f", "--file", type=str, required=True, help="JSON file name")
    args = parser.parse_args()
    main(**args.__dict__)
