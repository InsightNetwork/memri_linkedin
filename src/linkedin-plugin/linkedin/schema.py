""" Items to be stored in the pod. """
import enum
from typing import Optional

import tweepy
from pymemri.data import schema
from pymemri.data.schema import Item

SERVICE_NAME = "twitter"


class HashableItem(Item):
    def __hash__(self):
        if self.externalId is None:
            raise ValueError("Cannot hash item without externalId")
        return hash(self.__class__.__name__ + self.externalId)


class Account(HashableItem, schema.Account):
    service: Optional[str] = SERVICE_NAME
    description: Optional[str]
    followersCount: Optional[int]
    followingCount: Optional[int]
    tweetCount: Optional[int]
    listedCount: Optional[int]
    verified: Optional[bool]

    @classmethod
    def from_tweepy(cls, user: tweepy.User) -> "Account":
        if user.public_metrics is None:
            return cls(
                externalId=user.id,
                # service=SERVICE_NAME,
                displayName=user.name,
                handle=user.username,
                description=user.description,
                verified=user.verified,
            )
        return cls(
            externalId=user.id,
            # service=SERVICE_NAME,
            displayName=user.name,
            handle=user.username,
            description=user.description,
            followersCount=user.public_metrics["followers_count"],
            followingCount=user.public_metrics["following_count"],
            tweetCount=user.public_metrics["tweet_count"],
            listedCount=user.public_metrics["listed_count"],
            verified=user.verified,
        )


class TweetType(str, enum.Enum):
    TWEET = "tweet"
    RETWEET = "retweet"
    QUOTE = "quote"
    REPLY = "reply"

    @staticmethod
    def value_from_tweepy(tweet: tweepy.Tweet) -> str:
        str2tweettype = {
            "retweeted": TweetType.RETWEET,
            "quoted": TweetType.QUOTE,
            "replied_to": TweetType.REPLY,
        }

        if tweet.referenced_tweets is None:
            return TweetType.TWEET.value
        return str2tweettype.get(tweet.referenced_tweets[0].type, TweetType.TWEET).value


class Photo(schema.Photo, HashableItem):
    pass


class Tweet(HashableItem, schema.Tweet):
    service = SERVICE_NAME

    @classmethod
    def from_tweepy(cls, tweet: tweepy.Tweet) -> "Tweet":
        tweet_type = TweetType.value_from_tweepy(tweet)
        return cls(
            externalId=tweet.id,
            message=tweet.text,
            conversationId=tweet.conversation_id,
            # service=SERVICE_NAME,
            tweetType=tweet_type,  # type: ignore
            postDate=tweet.created_at,
            retweetCount=tweet.public_metrics["retweet_count"],
            replyCount=tweet.public_metrics["reply_count"],
            likeCount=tweet.public_metrics["like_count"],
        )
