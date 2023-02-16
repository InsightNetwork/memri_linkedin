import pytest
from conftest import get_premade_plugin
from pymemri import PodClient

from linkedin.schema import Account


def test_following():
    plugin = get_premade_plugin(import_data=False)
    plugin.import_friends()
    plugin.join()

    client = PodClient(
        owner_key=plugin.client.owner_key,
        database_key=plugin.client.database_key,
    )

    accounts = client.search_typed(Account)
    owner = [acc for acc in accounts if acc.following]
    assert len(owner) == 1
    assert len(owner[0].following)
    assert len(owner[0].follower)


@pytest.mark.xfail(reason="This is a bug in pymemri")
def test_following_client_duplicate():
    plugin = get_premade_plugin(import_data=False)
    plugin.import_friends()
    plugin.join()

    accounts = plugin.client.search_typed(Account)
    owner = [acc for acc in accounts if acc.follower]
    before_len_owner = len(owner)
    before_len_following = len(owner[0].following)
    before_len_follower = len(owner[0].follower)

    client = PodClient(
        owner_key=plugin.client.owner_key,
        database_key=plugin.client.database_key,
    )
    plugin.client.reset_local_db()
    accounts = client.search_typed(Account)
    owner = [acc for acc in accounts if acc.follower]
    assert len(owner) == before_len_owner
    assert len(owner[0].following) == before_len_following
    assert len(owner[0].follower) == before_len_follower
