import argparse
import json
from LinkedInGraph import LinkedInGraph


def main(file: str, owner_key: str, database_key: str):
    graph = LinkedInGraph(owner_key=owner_key, database_key=database_key,
                          create_account=False)

    persons = graph.get_persons()
    links = graph.get_links(persons)

    data = {
        "nodes": [i.to_json() for i in persons],
        "links": [{"source": i.source.id, "target": i.target.id,
                   "type": i.name} for i in links],
    }

    with open(file, "w") as f:
        sdata = json.dumps(data)
        f.write(sdata)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="memri -> JSON tool")
    parser.add_argument("-f", "--file", type=str, required=True,
                        help="JSON file name")
    parser.add_argument("--owner_key", type=str, required=True)
    parser.add_argument("--database_key", type=str, required=True)
    args = parser.parse_args()
    main(**args.__dict__)
