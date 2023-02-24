import argparse
import json
import os
from typing import List
from memri.LinkedInGraph import LinkedInGraph
from memri.schema import LinkedInAccount, LinkedInLink


ROOT = os.path.dirname(__file__)


def main(file: str, owner_key: str, database_key: str):
    accounts: List["LinkedInAccount"] = []
    links: List["LinkedInLink"] = []

    with open(os.path.join(ROOT, file)) as f:
        sdata = f.read()
        m = json.loads(sdata)

        for i in m["result"][0]["profiles"]:
            accounts.append(
                LinkedInAccount(
                    externalId=i["_id"],
                    handle=i["data"]["profile"]["username"],
                    displayName=i["data"]["profile"]["fullname"],
                    locationName=i["data"]["profile"].get("loc"),
                    description=i["data"]["profile"].get("desc"),
                    avatarUrl=i["data"]["profile"].get("image"),
                )
            )

        for i in m["result"][0]["edges"]:
            p1 = list(filter(lambda x: x.externalId == i[0], accounts))
            p2 = list(filter(lambda x: x.externalId == i[1], accounts))

            if p1 and p2:
                links.append(
                    LinkedInLink(
                        p1[0],
                        p2[0],
                        i[2],
                    )
                )

    graph = LinkedInGraph(owner_key=owner_key, database_key=database_key)
    graph.bulk_create(accounts=accounts, links=links)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON -> memri tool")
    parser.add_argument("-f", "--file", type=str, required=True,
                        help="JSON file name")
    parser.add_argument("--owner_key", type=str, required=True)
    parser.add_argument("--database_key", type=str, required=True)
    args = parser.parse_args()
    main(**args.__dict__)
