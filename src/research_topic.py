# src/cluster_document.py
import re
import json
import random
import os
from datetime import datetime
from google import genai
import sys
import time # ★変更点1: timeモジュールをインポート
from google.genai.errors import ServerError # ★変更点2: ServerErrorをインポート

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def load_json_file(file_path: str) -> dict:
    """JSONファイルを読み込み、Pythonの辞書として返す。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"エラー: ファイルが見つかりません - {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ★★★ ここから関数を丸ごと変更 ★★★
def research_and_summarize_with_gemini(topic_data: dict):
    """
    指定されたトピックについて、GeminiのGoogle Search機能で調査し、要約を生成する。
    503エラーなどのサーバーエラーが発生した場合、自動でリトライする。
    """
    api_key = config.GEMINI_API_KEY
    client = genai.Client(api_key=api_key)
    
    research_model = client.chats.create(
        model='gemini-2.0-flash-exp',
        config={'tools': [{'google_search': {}}]}
    )

    theme = topic_data['theme']
    keywords = ", ".join(topic_data['keywords'])

    prompt = f"""
    あなたは専門的な調査アシスタントです。
    以下のテーマとキーワードに基づいて、Webから信頼できる情報をリアルタイムで検索・収集してください。
    その上で、収集した情報を統合し、このトピックについて深く理解できるような解説文を生成してください。

    # 調査トピック
    - テーマ: {theme}
    - 関連キーワード: {keywords}

    # 出力形式
    ## 【トピック概要】
    (テーマについて、初心者にも分かるように簡潔に説明)

    # 出力形式
    必ず、以下のJSON形式で出力してください。
    ```json
    {{
    "overview": "(テーマについての簡潔な説明)",
    "details": "(背景や事例などの詳細な解説)",
    "trends": "(最新の動向や議論)",
    "tweet": "(X投稿用の100字程度の要約。あおる表現は使わず丁寧語ですます調。アンケート調査の話題は含めない。ハッシュタグは不要。)"
    }}
    """

    print("GeminiによるWeb調査と要約を開始します...")
    
    # リトライ処理用の設定
    max_retries = 3
    retry_delay = 10  # 待機時間（秒）

    # リトライ処理のループ
    for attempt in range(max_retries):
        try:
            print(f"Geminiに問い合わせています... (試行 {attempt + 1}/{max_retries})")
            response = research_model.send_message(prompt)
            print("Geminiからの応答を取得しました。")
            return response.text  # 成功したら結果を返してループを抜ける

        except ServerError as e:
            print(f"サーバーエラーが発生しました: {e}")
            if attempt < max_retries - 1:
                print(f"{retry_delay}秒待機して再試行します。")
                time.sleep(retry_delay)
            else:
                print("最大再試行回数に達しました。処理を中断します。")
                # 最終的に失敗した場合、エラーを発生させる
                raise ConnectionError(f"Gemini APIが繰り返し利用不能でした: {e}")
        
        except Exception as e:
            # ServerError以外の予期せぬエラーは即座に中断
            raise ConnectionError(f"Gemini APIとの通信中に予期せぬエラーが発生しました: {e}")
            
# ★★★ ここまでが変更箇所 ★★★


def save_knowledge_as_json(file_path: str, data_to_add: dict):
    """生成された知識をJSONファイルに追記する。"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {"knowledge_entries": []}
    else:
        all_data = {"knowledge_entries": []}
    
    all_data["knowledge_entries"].append(data_to_add)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"知識データを {file_path} に保存しました。")
    
if __name__ == "__main__":
    JSON_FILE_PATH = "./data/clustered_output.json"
    OUTPUT_JSON_PATH = "./data/knowledge_base/knowledge_entries.json"

    try:
        clustered_data = load_json_file(JSON_FILE_PATH)
        
        if clustered_data and "clusters" in clustered_data:
            selected_topic = random.choice(clustered_data["clusters"])
            
            print("--- 調査対象トピック ---")
            print(f"ID: {selected_topic['cluster_id']}")
            print(f"テーマ: {selected_topic['theme']}")
            print("------------------------\n")

            summary_result = research_and_summarize_with_gemini(selected_topic)
            
            print("\n--- 調査・要約結果 ---")
            print(summary_result)
            print("----------------------\n")

            match = re.search(r"```json\s*(\{.*?\})\s*```", summary_result, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                data = json.loads(json_str)

                tweet_text = data.get("tweet", "")
                if tweet_text:
                    print("--- 抽出されたツイート文 ---")
                    print(tweet_text)
                    print("--------------------------\n")

                knowledge_entry = {
                    "topic_id": selected_topic['cluster_id'],
                    "theme": selected_topic['theme'],
                    "keywords": selected_topic['keywords'],
                    "generated_tweet": tweet_text,
                    "created_at": datetime.now().isoformat()
                }
                save_knowledge_as_json(OUTPUT_JSON_PATH, knowledge_entry)
            else:
                print("エラー: Geminiの応答からJSONデータを抽出できませんでした。")

    except (FileNotFoundError, ValueError, ConnectionError, json.JSONDecodeError) as e:
        # メインのtry-exceptブロックで最終的なエラーをキャッチ
        print(f"エラーが発生しました: {e}")
