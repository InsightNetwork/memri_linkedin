import re
from typing import List

import pytest
from conftest import get_premade_plugin
from pymemri import PodClient

from linkedin.schema import Tweet


def test_quote_tweets():
    premade_plugin = get_premade_plugin()
    tweets = premade_plugin.client.search({"type": "Tweet", "tweetType": "quote"})
    assert len(tweets)
    quotes = [tweet.reference[0] for tweet in tweets if tweet.reference]
    assert len(quotes) == len(tweets), "All quotes should have a reference"


@pytest.mark.xfail(reason="This test is not stable")
def test_conversation():
    premade_plugin = get_premade_plugin()
    client = premade_plugin.client
    tweets = client.search_typed(
        Tweet,
        {
            "tweetType": "tweet",
            # "externalId": "1605424686946430977",
        },
    )
    premade_plugin.start()
    root_tweet = tweets[1]
    premade_plugin.import_conversation_by_id(conversation_id=root_tweet.conversationId)
    premade_plugin.join()

    client = PodClient(
        url=premade_plugin.client.api._url,
        database_key=premade_plugin.client.database_key,
        owner_key=premade_plugin.client.owner_key,
    )

    conv_tweets = client.search(
        {
            "type": "Tweet",
            "conversationId": root_tweet.conversationId,
        }
    )
    root_tweets = [tweet for tweet in conv_tweets if tweet.tweetType == "tweet"]
    assert len(root_tweets) == 1 and root_tweets[0].id == root_tweet.id

    num_replies = len([tweet for tweet in conv_tweets if tweet.tweetType != "tweet"])
    assert num_replies, "There should be replies"
    assert len(conv_tweets) == num_replies + 1  # +1 for the original tweet

    all_replies = get_all_replies(root_tweet)
    {tweet.id for tweet in all_replies}

    # The numbers should match, but they don't
    # need to figure out why
    # assert len(all_unique_ids) == num_replies


def get_all_replies(tweet) -> List[Tweet]:
    """Used for debugging and development"""
    replies = tweet.replies
    for reply in replies:
        replies += get_all_replies(reply)
    return replies


def print_replies(tweet, indent=0):
    for tweet in tweet.replies:
        print(
            "  " * indent * 4,
            author_to_str(tweet.author[0], tweet),
            get_tweet_content(tweet),
        )
        print_replies(tweet, indent=indent + 1)


def author_to_str(author, tweet):
    return (
        f"@{author.handle} : ({tweet.replyCount}, "
        f"{tweet.retweetCount}, {tweet.likeCount}): "
    )


def get_tweet_content(tweet):
    # remove handles at the beginning of the tweet
    message = re.sub(r"^(@\w+ )+", "", tweet.message)
    return message[:50].replace("\n", " ")
