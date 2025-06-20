# main_poster.py
# 情報収集・投稿機能の実装予定

import json
import random
import datetime
import google.generativeai as genai
import tweepy # X APIライブラリ (例: tweepy)
from pathlib import Path
import config # config.pyをインポート

# Gemini APIキーの設定
genai.configure(api_key=config.GEMINI_API_KEY)

# X APIクライアントの設定 (tweepy v2 OAuth 2.0 Bearer Tokenの例)
# client = tweepy.Client(bearer_token=config.X_BEARER_TOKEN)

# tweepy v1.1 (OAuth 1.0a) の場合
auth = tweepy.OAuth1UserHandler(
   config.X_API_KEY, config.X_API_KEY_SECRET,
   config.X_ACCESS_TOKEN, config.X_ACCESS_TOKEN_SECRET
)
api_v1 = tweepy.API(auth)

# tweepy v2 (OAuth 1.0a) の場合
client_v2 = tweepy.Client(
    consumer_key=config.X_API_KEY,
    consumer_secret=config.X_API_KEY_SECRET,
    access_token=config.X_ACCESS_TOKEN,
    access_token_secret=config.X_ACCESS_TOKEN_SECRET
)


def load_clusters(file_path: str) -> list[dict]:
    """
    クラスタ情報が保存されたJSONファイルを読み込む。
    """
    cluster_file = Path(file_path)
    try:
        with open(cluster_file, 'r', encoding='utf-8') as f:
            clusters = json.load(f)
        return clusters
    except FileNotFoundError:
        print(f"Error: Cluster file not found at {cluster_file}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {cluster_file}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading clusters: {e}")
        return []

def select_theme(clusters: list[dict], post_history: list[dict]) -> dict | None:
    """
    投稿するテーマを選択する。
    （例: 過去に投稿していないテーマ、またはランダムに選択）
    """
    if not clusters:
        return None
    return random.choice(clusters)


def search_related_information(theme_name: str, theme_summary: str) -> list[str]:
    """
    GeminiのGoogle Search機能（またはそれに類する機能）で関連情報を収集する。
    この関数はGeminiの具体的な検索ツールAPIの仕様に依存します。
    """
    print(f"Searching for information related to theme: {theme_name}")
    dummy_search_results = [
        f"最新情報1: {theme_name}に関する新しい発見がありました。",
        f"関連ニュース: {theme_summary}についての議論が活発です。",
        f"ブログ記事: {theme_name}の応用例について解説します。"
    ]
    print(f"Found information: {dummy_search_results}")
    return dummy_search_results


def generate_tweet_text(theme_name: str, theme_summary: str, search_results: list[str]) -> str | None:
    """
    収集した情報とテーマを基に、X投稿用のツイート文を生成する。
    """
    if not search_results:
        search_info = "関連情報は現在見つかりませんでした。"
    else:
        search_info = "\n".join([f"- {res}" for res in search_results[:3]])

    prompt = f"""以下のテーマと関連情報に基づいて、X(旧Twitter)に投稿するための魅力的で簡潔なツイート文を1つ生成してください。
ツイートは最大でも130字程度に収めてください。ハッシュタグをいくつか含めてください。

テーマ名: {theme_name}
テーマ要約: {theme_summary}

関連情報:
{search_info}

ツイート文案:
"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        tweet_text = response.text.strip()
        return tweet_text
    except Exception as e:
        print(f"Error during tweet generation with Gemini: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Gemini response text: {response.text}")
        return None

def post_to_x(tweet_text: str) -> str | None:
    """
    生成されたツイートをX APIを利用して投稿する。
    成功した場合、投稿ID (またはURL) を返す。
    """
    if not tweet_text:
        print("No tweet text to post.")
        return None
    try:
        response = client_v2.create_tweet(text=tweet_text)
        print(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
        return str(response.data['id'])
    except tweepy.TweepyException as e:
        print(f"Error posting tweet to X: {e}")
        return None

def record_post_history(theme_name: str, tweet_text: str, post_id: str | None, history_file_path: str):
    """
    投稿日時、ツイート内容、元になったテーマ等の情報をJSONファイルに追記する。
    """
    history_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "theme_name": theme_name,
        "tweet_text": tweet_text,
        "post_id": post_id,
        "status": "success" if post_id else "failed"
    }
    
    history_path = Path(history_file_path)
    history_path.parent.mkdir(parents=True, exist_ok=True)

    history_data = []
    if history_path.exists():
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode existing post history file at {history_path}. Starting with a new list.")
            history_data = []
        except Exception as e:
            print(f"An unexpected error occurred while reading post history: {e}")
            history_data = []

    history_data.append(history_entry)
    
    try:
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        print(f"Post history updated in {history_path}")
    except Exception as e:
        print(f"Error saving post history to {history_path}: {e}")


def load_post_history(file_path: str) -> list[dict]:
    """
    投稿履歴ファイルを読み込む。
    """
    history_file = Path(file_path)
    if not history_file.exists():
        return []
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return history
    except Exception as e:
        print(f"Error loading post history: {e}")
        return []


if __name__ == '__main__':
    print("Starting main poster process...")

    clusters_file = config.CLUSTERS_FILE
    history_file = config.POST_HISTORY_FILE

    clusters = load_clusters(clusters_file)
    if not clusters:
        print("No clusters loaded. Exiting.")
    else:
        post_history = load_post_history(history_file)
        selected_theme = select_theme(clusters, post_history)
        
        if selected_theme:
            theme_name = selected_theme.get("theme_name", "N/A")
            theme_summary = selected_theme.get("summary", "")
            print(f"Selected theme: {theme_name}")

            related_info = search_related_information(theme_name, theme_summary)
            tweet = generate_tweet_text(theme_name, theme_summary, related_info)

            if tweet:
                print(f"Generated tweet: {tweet}")
                posted_tweet_id = post_to_x(tweet)
                record_post_history(theme_name, tweet, posted_tweet_id, history_file)
            else:
                print("Failed to generate tweet.")
                record_post_history(theme_name, "Failed to generate tweet text.", None, history_file)
        else:
            print("No theme selected for posting.")
            
    print("Main poster process finished.")
