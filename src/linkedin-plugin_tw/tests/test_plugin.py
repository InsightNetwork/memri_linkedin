import pytest
from conftest import get_premade_plugin, get_premade_pod

from linkedin import PodClient
from linkedin.schema import Account, Tweet


@pytest.mark.timeout(20)
def test_benchmark():
    premade_pod = get_premade_pod()
    # values are hard coded wrt to the test data
    tweets = premade_pod.search({"type": "Tweet"})
    assert len(tweets)
    assert len([tweet.author[0] for tweet in tweets if tweet.author]) == len(tweets)
    accounts = premade_pod.search({"type": "Account"})
    assert len([tweet.photo[0] for tweet in tweets if tweet.photo])
    assert len(accounts)
    assert len(
        [author.profilePicture[0] for author in accounts if author.profilePicture]
    ) == len(accounts)

    liked_tweets = premade_pod.search({"type": "Tweet", "liked": True})
    assert len(liked_tweets)


@pytest.mark.timeout(20)
def test_duplicates():
    plugin = get_premade_plugin()

    before_tweets = plugin.client.search_typed(Tweet)
    before_accounts = plugin.client.search_typed(Account)
    assert len(before_tweets) == len(
        {tweet.externalId for tweet in before_tweets}
    ), "There are duplicate tweets in the pod"
    assert len(before_accounts) == len(
        {account.externalId for account in before_accounts}
    ), "There are duplicate accounts in the pod"

    client = PodClient(
        url=plugin.client.api._url,
        owner_key=plugin.client.owner_key,
        database_key=plugin.client.database_key,
    )
    plugin = get_premade_plugin(client=client, import_data=False)
    plugin.sync()
    plugin.join()

    after_tweets = client.search({"type": "Tweet"})
    after_accounts = client.search({"type": "Account"})

    assert len(before_tweets) == len(after_tweets)
    assert len(before_accounts) == len(after_accounts)
