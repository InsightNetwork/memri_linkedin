import pytest
from assets import ASSETS_PATH
from pymemri.data.basic import read_json
from pymemri.pod.client import PodClient
from tweepy.client import Response, User

from linkedin import LinkedinPlugin


@pytest.mark.timeout(20)
def test_tweepy_none():
    class NoneAPI:
        def none_response_func(*args, **kwargs):
            return Response(None, {}, [], {})

        get_home_timeline = none_response_func
        get_user = none_response_func
        get_tweet = none_response_func
        get_users_following = none_response_func
        get_users_followers = none_response_func

        def get_me(self, *args, **kwargs):
            json_data = read_json(str(ASSETS_PATH / "json_cache" / "me.json"))
            user = User(json_data["data"])
            return Response(user, {}, [], {})

    client = PodClient()
    client.get_oauth2_access_token = lambda platform: "FAKE_TOKEN"

    plugin = LinkedinPlugin(client=client)

    plugin.add_to_schema()
    plugin.tweepy_producer._client = NoneAPI()
    plugin.sync()
    plugin.join()
    plugin.teardown()

    tweets = client.search({"type": "Tweet"})
    assert len(tweets) == 0
