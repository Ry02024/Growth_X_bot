# main.py
import random
import argparse
from pathlib import Path
import config
from src import llm_handler, x_poster, utils, cluster_generator


def select_theme(clusters: list[dict], post_history: list[dict]) -> dict | None:
    """
    投稿するテーマをランダムに選択する。
    """
    # TODO: 最近投稿したテーマを避けるなど、より高度な選択ロジックを実装する
    if not clusters:
        return None
    return random.choice(clusters)


def main():
    """
    ボットのメイン処理フロー
    """
    parser = argparse.ArgumentParser(description="Growth_X_bot: AI-powered X poster.")
    parser.add_argument(
        '--force-recluster',
        action='store_true',
        help='Force the clustering process to run, even if a cluster file exists.'
    )
    args = parser.parse_args()

    print("--- Starting Growth_X_bot ---")

    # 1. 必要であればクラスタリングを実行
    if not cluster_generator.generate_clusters_if_needed(force_recluster=args.force_recluster):
        print("--- Growth_X_bot finished (due to clustering issue) ---")
        return

    # 2. 投稿テーマの選択
    clusters = utils.load_clusters(config.CLUSTERS_FILE)
    if not clusters:
        print("No clusters loaded. Exiting.")
        print("--- Growth_X_bot finished ---")
        return

    post_history = utils.load_post_history(config.POST_HISTORY_FILE)
    selected_theme = select_theme(clusters, post_history)

    if not selected_theme:
        print("No theme could be selected for posting.")
        print("--- Growth_X_bot finished ---")
        return

    theme_name = selected_theme.get("theme_name", "N/A")
    theme_summary = selected_theme.get("summary", "")
    print(f"Selected theme: {theme_name}")

    # 3. ツイート生成、投稿、履歴記録
    related_info = llm_handler.search_related_information(theme_name, theme_summary)
    tweet = llm_handler.generate_tweet_text(theme_name, theme_summary, related_info)

    if tweet:
        print(f"Generated tweet:\n---\n{tweet}\n---")
        # X (旧Twitter) への投稿を一時的にスキップします。
        # 実際に投稿するには、以下の2行のコメントアウトを解除してください。
        print("X (旧Twitter) への投稿は現在スキップされています (Gemini APIのみモード)。")
        posted_id = None # 投稿していないため、post_idはNoneとします
        # client = x_poster.get_x_client()
        # posted_id = x_poster.post_to_x(client, tweet)
        utils.record_post_history(theme_name, tweet, posted_id, config.POST_HISTORY_FILE)

    print("--- Growth_X_bot finished ---")

if __name__ == '__main__':
    main()