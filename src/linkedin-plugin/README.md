# Twitter Plugin


## About
This plugin is designed on top of the [Twitter API](https://developer.twitter.com) V2 with [OAuth 1.0a flow](https://developer.twitter.com/en/docs/authentication/oauth-1-0a).
The twitter API uses OAuth 2.0.
The plugin is accessing the twitter API using [tweepy](http://docs.tweepy.org/) an easy-to-use Python library for accessing the Twitter API

## Data imported
In this plugin, the data fetched for a given user handle includes:
- User timeline tweets (id, content, mentions (only if already processed), date, author)

## Data to be imported
- User account (id, handle, name, description, profile picture)
- Followers and following accounts (id, handle, name, description, profile picture)

### Building the Docker image

### Development flow
### Development flow

```
    pip install -e .[dev]
    pre-commit install
```

Make sure to have pod running locally with the following environment variables set,
or use the dev pod at https://dev.pod.memri.io.
```
TWITTER_V2_CLIENT_ID
TWITTER_V2_CLIENT_SECRET
```

Your pod needs an access token to run the plugin.
Get an access token by running the following command.
```
    twitter-oauth
```
This will open a browser window and ask you to login to twitter and 
authorize the pod defined by keys.json


Using dev pod? Then run:
```
    twitter-oauth --pod dev
```

Now you can run the plugin locally by running the following command:
```
    run_plugin --metadata metadata.json
```

### To run tests
    pytest ./tests/


