# src/x_poster.py
import tweepy
import config


def get_x_client() -> tweepy.Client:
    """
    Tweepy v2 clientを初期化して返す。
    """
    try:
        return tweepy.Client(
            consumer_key=config.X_API_KEY,
            consumer_secret=config.X_API_KEY_SECRET,
            access_token=config.X_ACCESS_TOKEN,
            access_token_secret=config.X_ACCESS_TOKEN_SECRET
        )
    except Exception as e:
        raise RuntimeError("Failed to initialize Tweepy client. Check your X API keys in the .env file.") from e


def post_to_x(client: tweepy.Client, tweet_text: str) -> str | None:
    """
    生成されたツイートをX APIを利用して投稿する。成功した場合、投稿IDを返す。
    """
    try:
        response = client.create_tweet(text=tweet_text)
        return str(response.data['id'])
    except tweepy.TweepyException as e:
        print(f"Error posting tweet to X: {e}")
        return None