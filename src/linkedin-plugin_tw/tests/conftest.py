import os

import pytest
from cached_session import CachedSession

from linkedin import PodClient, LinkedinPlugin
from linkedin.schema import Account, Photo, Tweet


@pytest.fixture(scope="function")
def plugin():
    client = PodClient()
    client.add_to_schema(Account, Tweet, Photo)

    # Set TWITTER_ACCESS_TOKEN to update the cached session
    client.get_oauth2_access_token = lambda platform: os.environ.get(
        "TWITTER_ACCESS_TOKEN", "FAKE_TOKEN"
    )

    plugin = LinkedinPlugin(client=client)
    cached_session = CachedSession("tests/assets/test_benchmark")
    plugin.tweepy_producer._client.session = cached_session
    plugin.session = cached_session

    plugin.add_to_schema()

    yield plugin

    plugin.join()


def get_premade_pod():
    plugin = get_premade_plugin()

    client = PodClient(
        url=plugin.client.api._url,
        owner_key=plugin.client.owner_key,
        database_key=plugin.client.database_key,
    )
    client.get_oauth2_access_token = lambda platform: os.environ.get(
        "TWITTER_ACCESS_TOKEN", "FAKE_TOKEN"
    )
    return client


def get_premade_plugin(client=None, import_data=True) -> LinkedinPlugin:
    cache_path = "tests/assets/test_collection"
    client = client or PodClient()
    client.add_to_schema(Account, Tweet, Photo)

    # Set TWITTER_ACCESS_TOKEN to update the cached session
    client.get_oauth2_access_token = lambda platform: os.environ.get(
        "TWITTER_ACCESS_TOKEN", "FAKE_TOKEN"
    )

    plugin = LinkedinPlugin(client=client)
    cached_session = CachedSession(cache_path)
    plugin.tweepy_producer._client.session = cached_session
    plugin.session = cached_session

    plugin.add_to_schema()
    if import_data:
        plugin.sync()
        plugin.join()
    return plugin
