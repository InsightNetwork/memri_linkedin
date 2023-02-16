import json
import os
import threading
from dataclasses import dataclass
from time import sleep, time

import pytest
from assets import ASSETS_PATH
from loguru import logger
from pymemri.data.basic import read_json
from pymemri.data.schema import Account, OauthFlow, PluginRun
from pymemri.plugin.pluginbase import PluginBase
from pymemri.pod.client import PodClient
from tweepy.api import pagination
from tweepy.client import Media, Place, Poll, Response, Tweet, User

from linkedin import LinkedinPlugin
from linkedin.schema import SERVICE_NAME


@dataclass
class Context:
    run: PluginRun
    pod: PodClient
    plugin_thread: threading.Thread
    plugin: PluginBase


def create_plugin_thread(plugin: LinkedinPlugin):
    def start_plugin():
        plugin._run()

    # Run plugin on separate thread
    plugin_thread = threading.Thread(target=start_plugin)

    return plugin_thread


@pytest.fixture
def context():
    run = PluginRun(
        containerImage="",
    )

    credentials_str = os.environ["TWITTER_CI_CREDENTIALS"]
    credentials = json.loads(credentials_str)
    oauth = OauthFlow(
        accessToken=credentials["access_token"],
        accessTokenSecret=credentials["access_token_secret"],
        service=SERVICE_NAME,
    )
    me = Account(
        service=SERVICE_NAME,
        isMe=True,
        identifier=credentials["access_token"],
        secret=credentials["access_token_secret"],
    )

    pod = PodClient()
    twitter_plugin = LinkedinPlugin(client=pod, pluginRun=run)
    twitter_plugin.add_to_schema()

    pod.create(run)
    pod.create(me)
    pod.create(oauth)

    twitter_thread = threading.Thread(target=twitter_plugin._run)

    yield Context(run, pod, twitter_thread, twitter_plugin)

    # Tear down
    twitter_plugin.running = False
    with twitter_plugin.cv:
        twitter_plugin.cv.notify()

    if twitter_thread.is_alive():
        twitter_thread.join()
    twitter_plugin.teardown()


@pytest.mark.skip(reason="Need to setup OAuth2 credentials for CI")
def test_plugin_with_real_account(context: Context):
    context.plugin_thread.start()

    timeout = time() + 60 * 5  # 5 minutes from now

    # Plugin should start importing the data
    logger.info("Waiting to import all the data...")
    while True:

        logger.warning(f"progress {context.run.progress}")

        if context.run.progress == 1:
            logger.info("Successfully imported all the data")
            # we need to wait untill the photos are uploaded
            sleep(5)
            break

        if time() > timeout:
            pytest.fail(
                "Plugin did not import data in reasonable amount of time, ",
                "stuck at progress {context.run.progress}",
            )
        sleep(0.2)

    # test data is in the pod
    me = context.pod.search({"service": SERVICE_NAME, "isMe": True})[0]
    accounts = context.pod.search({"service": SERVICE_NAME, "type": "Account"})
    tweets = context.pod.search({"service": SERVICE_NAME, "type": "Tweet"})
    photos = context.pod.search({"type": "Photo"})

    logger.info("#Accounts", len(accounts))
    logger.info("#Tweets", len(tweets))
    logger.info("#Images", len(photos))

    assert not me.handle
    assert not me.displayName
    assert len(accounts) > 1
    assert len(tweets) > 1
    assert len(photos) > 1


@pytest.mark.timeout(20)
def test_first_processing():
    class MockAPI:
        def __init__(self):
            self.memri_json_data = read_json(
                str(ASSETS_PATH / "json_cache" / "home_timeline.json")
            )

        def _process_includes(self, includes):
            if "media" in includes:
                includes["media"] = [Media(media) for media in includes["media"]]
            if "places" in includes:
                includes["places"] = [Place(place) for place in includes["places"]]
            if "polls" in includes:
                includes["polls"] = [Poll(poll) for poll in includes["polls"]]
            if "tweets" in includes:
                includes["tweets"] = [Tweet(tweet) for tweet in includes["tweets"]]
            if "users" in includes:
                includes["users"] = [User(user) for user in includes["users"]]
            return includes

        @pagination(mode="next")
        def get_home_timeline(self, *args, **kwargs):
            # sleep(0.63 + 0.71 + 0.75 + 0.65 + 0.24)
            json_data = read_json(
                str(ASSETS_PATH / "json_cache" / "home_timeline.json")
            )
            data = [Tweet(result) for result in json_data["data"]]
            includes = self._process_includes(json_data["includes"])
            errors = json_data.get("errors", [])
            meta = json_data["meta"]
            return Response(data, includes, errors, meta)

        def get_me(self, *args, **kwargs):
            json_data = read_json(str(ASSETS_PATH / "json_cache" / "me.json"))
            user = User(json_data["data"])
            return Response(user, {}, [], {})

        def get_user(self, *args, **kwargs):
            json_data = read_json(str(ASSETS_PATH / "json_cache" / "user.json"))
            user = User(json_data["data"])
            return Response(user, {}, [], {})

        def get_tweet(self, id, **kwargs):
            # Ugly hack to return a single tweet
            return Response(Tweet(self.memri_json_data["data"][0]), None, None, None)

        def get_users_following(self, *args, **kwargs):
            response = self.get_user(*args, **kwargs)
            return Response([response.data], {}, [], {})

        def get_users_followers(self, *args, **kwargs):
            response = self.get_user(*args, **kwargs)
            return Response([response.data], {}, [], {})

    start = time()
    client = PodClient()
    client.get_oauth2_access_token = lambda platform: "FAKE_TOKEN"

    plugin = LinkedinPlugin(client=client)

    # cached_session = JsonCachedSession("tests/assets/json_cache")
    # plugin.tweepy_producer.client.session = cached_session

    plugin.add_to_schema()
    plugin.tweepy_producer._client = MockAPI()
    plugin.sync()
    plugin.join()
    delta = time() - start
    plugin.teardown()

    tweets = client.search({"type": "Tweet"})
    assert len(tweets)
    print(f"{delta:.2f} seconds spent on importing")
