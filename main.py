import sys
import random
import os

# srcディレクトリをPythonの検索パスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 作成したモジュールから必要な関数をインポート
from llm_handler import research_and_generate_content
from file_handler import load_json, save_knowledge_entry
from x_poster import post_to_x, trim_to_140_chars

# --- 設定 ---
TOPIC_SOURCE_FILE = "data/clustered_output.json"
KNOWLEDGE_BASE_FILE = "data/knowledge_base/knowledge_entries.json"

def main():
    """
    一連のボット処理を実行するメイン関数
    """
    try:
        # 1. トピックの選択
        print("1. トピックを選択しています...")
        all_topics = load_json(TOPIC_SOURCE_FILE)
        if not all_topics.get("clusters"):
            print("エラー: トピックソースに有効なクラスタが見つかりません。")
            return
        selected_topic = random.choice(all_topics["clusters"])
        print(f"   選ばれたテーマ: 「{selected_topic['theme']}」")

        # 2. Web調査とコンテンツ生成
        print("\n2. Web調査とコンテンツ生成を実行します...")
        generated_content = research_and_generate_content(selected_topic)

        # 3. 知識の蓄積
        print("\n3. 生成された知識を保存します...")
        save_knowledge_entry(KNOWLEDGE_BASE_FILE, selected_topic, generated_content)

        # 4. ツイート文の準備と投稿
        print("\n4. Xへの投稿を準備します...")
        tweet_text = generated_content.get("tweet")
        if not tweet_text:
            print("エラー: 生成されたコンテンツにツイート文が含まれていません。")
            return
            
        final_tweet = trim_to_140_chars(tweet_text)
        print(f"   投稿するツイート: {final_tweet}")
        
        # ユーザーに最終確認
        if input("   この内容で投稿しますか？ (y/n): ").lower() == 'y':
            post_to_x(final_tweet)
        else:
            print("   投稿はキャンセルされました。")

        print("\n✨ 全ての処理が正常に完了しました！")

    except Exception as e:
        print(f"\n❌ 処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()