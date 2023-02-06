"""Tweepy wrapper."""
from dataclasses import dataclass
from functools import cache
from typing import Callable, Dict, Iterator, List, Optional

import tweepy
from loguru import logger

from .config import MAX_RESULTS, PAGE_LIMIT

TWEET_FIELDS = [
    "conversation_id",
    "in_reply_to_user_id",
    "public_metrics",
    "author_id",
    "created_at",
    "entities",
    "referenced_tweets",
]
USER_FIELDS = [
    "id",
    "name",
    "username",
    "description",
    "entities",
    "profile_image_url",
    "public_metrics",
    "verified",
]
MEDIA_FIELDS = [
    "media_key",
    "type",
    "url",
    "preview_image_url",
]

EXPANSIONS = [
    "referenced_tweets.id",
    "referenced_tweets.id.author_id",
    "attachments.media_keys",
]

TWEET_PAGINATOR_KWARGS = dict(
    user_auth=False,  # means API v2
    tweet_fields=TWEET_FIELDS,
    user_fields=USER_FIELDS,
    expansions=EXPANSIONS,
    max_results=MAX_RESULTS,  # max results per request
    media_fields=MEDIA_FIELDS,
)

# Patch tweepy.Tweet to have .id as a string
tweepy.Tweet.id_str = property(lambda self: str(self.id))
tweepy.User.id_str = property(lambda self: str(self.id))
tweepy.Tweet.author_id_str = property(lambda self: str(self.author_id))
tweepy.User.id_str = property(lambda self: str(self.id))


@dataclass
class Timeline:
    users: List[tweepy.User]


class TweepyProducer:
    def __init__(
        self,
        access_token: str,
    ) -> None:
        """Initialize a Tweepy client with an access token.

        Args:
            access_token: Twitter API v2 access token.
            session: A requests session to use for requests.
            If not provided, a new session will be created.
        """
        self._client = tweepy.Client(bearer_token=access_token)
        self.tweets_cache: Dict[str, tweepy.Tweet] = dict()
        self.users_cache: Dict[str, tweepy.User] = dict()
        self.media_cache: Dict[str, tweepy.Media] = dict()

    def get_user(self, *, id: str) -> tweepy.User:
        if id not in self.users_cache:
            self.users_cache[id] = self._client.get_user(
                id=id,
                user_fields=USER_FIELDS,
            ).data
        return self.users_cache[id]

    @cache
    def get_me(self) -> Optional[tweepy.User]:
        result = self._client.get_me(
            user_auth=False,
            user_fields=USER_FIELDS,
        )
        if result.data is None:
            return None
        return self.get_user(id=result.data.id)

    def get_user_following(self, *, user_id: str) -> Iterator[tweepy.User]:
        return self._get_user_connections(
            user_id=user_id, func=self._client.get_users_following
        )

    def get_user_followers(self, *, user_id: str) -> Iterator[tweepy.User]:
        return self._get_user_connections(
            user_id=user_id, func=self._client.get_users_followers
        )

    def _get_user_connections(
        self, *, user_id: str, func: Callable
    ) -> Iterator[tweepy.User]:
        for page in tweepy.Paginator(
            func,
            limit=PAGE_LIMIT,  # num requests to make to the API
            id=user_id,
            user_fields=USER_FIELDS,
        ):
            yield from page.data or []

    @property
    def access_token(self) -> str:
        return self._client.access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        old_session = self._client.session
        self._client = tweepy.Client(bearer_token=value)
        self._client.session = old_session
