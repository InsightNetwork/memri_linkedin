import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Condition, Lock
from typing import List, Optional, Type, Union

import requests
import tweepy
from loguru import logger
from pymemri.plugin.pluginbase import PluginBase
from pymemri.pod.client import PodClient
from pymemri.webserver.public_api import register_endpoint

from linkedin.pod_update_queue import PodQueue

from .config import SKIP_PHOTOS
from .consumer import ItemConsumer
from .schema import SERVICE_NAME, Account, Item, Photo, Tweet, TweetType
from .tweepy_util import TweepyProducer

THROTTLE = 5 * 60


def thread_safe(func):
    mutex = Lock()

    def wrapper(*args, **kwargs):
        with mutex:
            return func(*args, **kwargs)

    return wrapper


def run_delayed(func, delay):
    time.sleep(delay)
    logger.info(f"Running delayed function {func}")
    return func()


class LinkedinPlugin(PluginBase):
    def __init__(self, client: PodClient, *args, **kwargs) -> None:
        super().__init__(*args, client=client, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.session = requests.Session()
        self.cv = Condition()

        self.pod_queue = PodQueue()
        self.pod_update_consumer = ItemConsumer(
            client=self.client,
            queue=self.pod_queue,
            plugin_run=self.pluginRun,
        )
        self.pod_update_consumer.start()
        self.tweets_in_pod = {tw.externalId: tw for tw in client.search_typed(Tweet)}
        self.accounts_in_pod = {
            acc.externalId: acc for acc in client.search_typed(Account)
        }
        self.futures: List[Future] = []

        access_token = self.client.get_oauth2_access_token(platform=SERVICE_NAME)
        if access_token is None:
            raise RuntimeError(
                (
                    "No access token found in pod, did you authorize?"
                    "For development, you can run the CLI tool (twitter-oauth) "
                    "to setup your pod."
                )
            )
        self.tweepy_producer = TweepyProducer(
            access_token=access_token,
        )

    def update_access_token(self):
        # NOTE: Access token is updated in the pod, after each call
        self.tweepy_producer.access_token = self.client.get_oauth2_access_token(
            platform=SERVICE_NAME
        )

    def add_to_schema(self):
        return self.client.add_to_schema(
            Account,
            Item,
            Photo,
            Tweet,
        )

    def run(self):
        try:
            while True:

                # incremental progress updates are handled by pod_update_consumer
                # we set progress to 1 after a while
                # to handle the case where
                # there are less than expected number of tweets
                threading.Thread(
                    target=lambda: run_delayed(lambda: self.set_progress(1), delay=10)
                ).start()

                self.sync()
                with self.cv:
                    self.cv.wait(timeout=THROTTLE)
                self.update_access_token()

        except KeyboardInterrupt:
            logger.warning("Received SIGINT")
        except Exception as e:
            logger.exception(f"Error while collecting data: {e}")
            time.sleep(1)
        finally:
            self.wait_for_futures()
            self.join()
            logger.info("[+] Twitter plugin run is completed")

    def join(self):
        """only called when the plugin is stopped"""
        self.pod_update_consumer.join()

    def start(self):
        self.pod_update_consumer.start()

    def sync(self):
        logger.info("Tweets are imported")
        logger.info("Importing friends")
        self.import_friends()

        logger.info("Waiting for futures to complete")
        self.wait_for_futures()
        logger.info("Futures are completed")

    def wait_for_futures(self):
        logger.info("Waiting for futures to complete and join consumer thread")
        for future in self.futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error in future: {e}")

    def submit(self, func, *args, **kwargs) -> Future:
        future = self.executor.submit(func, *args, **kwargs)
        self.futures.append(future)
        return future

    def is_external_id_in_pod(
        self, item_type: Type[Union[Tweet, Account]], external_id: str
    ) -> bool:
        if item_type == Tweet:
            return external_id in self.tweets_in_pod
        elif item_type == Account:
            return external_id in self.accounts_in_pod
        else:
            raise ValueError(f"Unknown item type: {item_type}")

    def add_account_edge(
        self, owner: Account, tweepy_user: tweepy.User, edge_type: str
    ):
        if edge_type not in ["following", "follower"]:
            raise ValueError(f"Unknown edge type: {edge_type}")
        account = self.create_account(tweepy_user)
        edge = owner.add_edge(edge_type, account)
        self.pod_queue.put(update_items=[owner], create_edges=[edge])

    @thread_safe
    def create_account(self, tweepy_user: tweepy.User) -> Account:
        if not self.is_external_id_in_pod(Account, tweepy_user.id_str):
            account = Account.from_tweepy(tweepy_user)
            self.accounts_in_pod[tweepy_user.id_str] = account
            self.pod_queue.put(
                create_items=[account],
            )
            self.submit(
                self.add_profile_picture_edge,
                account=account,
                tweepy_user=tweepy_user,
            )
        return self.accounts_in_pod[tweepy_user.id_str]

    def add_profile_picture_edge(self, account: Account, tweepy_user: tweepy.User):
        if SKIP_PHOTOS:
            return

        self.add_photo_edge_from_url(
            item=account,
            external_id=tweepy_user.id_str,
            url=tweepy_user.profile_image_url,
        )

    def add_photo_edge_from_url(
        self,
        *,
        item: Union[Account, Tweet],
        external_id: str,
        url: str,
    ):
        response = self.session.get(url)
        if response.status_code != 200:
            logger.warning(f"Error while getting image from {url}")
            return

        edge_name = "profilePicture" if isinstance(item, Account) else "photo"
        photo = Photo.from_bytes(response.content)  # type: ignore
        photo.externalId = str(external_id)
        photo.file[0].externalId = str(external_id)

        try:
            edge = item.add_edge(edge_name, photo)
        except AssertionError as e:
            # Sometimes an error thrown by pydantic
            # reason unknown
            logger.error(e)
            return

        self.pod_queue.put(
            create_items=[photo, photo.file[0]],
            update_items=[item],
            create_edges=[edge, *(file for file in photo.get_edges("file"))],
        )

    def add_photo_edge(self, tweet: Tweet, tweepy_tweet: tweepy.Tweet):
        if (
            not tweepy_tweet.entities
            or tweepy_tweet.entities.get("urls") is None
            or tweepy_tweet.entities["urls"][0].get("media_key") is None
            or SKIP_PHOTOS
        ):
            return

        media_key = tweepy_tweet.entities["urls"][0]["media_key"]
        tweepy_media = self.tweepy_producer.get_media(media_key=media_key)
        if not tweepy_media or tweepy_media.type != "photo":
            return

        self.add_photo_edge_from_url(
            item=tweet,
            external_id=tweepy_tweet.id_str,
            url=tweepy_media.url,
        )

    def import_friends(self):
        """Imports the following accounts for the given account."""
        me = self.tweepy_producer.get_me()
        if me is None:
            logger.error("Could not get me, aborting import_friends")
            return
        owner = self.create_account(me)
        for tweepy_user in self.tweepy_producer.get_user_following(user_id=me.id):
            self.add_account_edge(owner, tweepy_user, "following")
        for tweepy_user in self.tweepy_producer.get_user_followers(user_id=me.id):
            self.add_account_edge(owner, tweepy_user, "follower")
