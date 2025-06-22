# src/cluster_document.py
import os, re
import json
import random
from datetime import datetime
from google import genai
from dotenv import load_dotenv

def load_json_file(file_path: str) -> dict:
    """JSONファイルを読み込み、Pythonの辞書として返す。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"エラー: ファイルが見つかりません - {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def research_and_summarize_with_gemini(topic_data: dict):
    """
    指定されたトピックについて、GeminiのGoogle Search機能で調査し、要約を生成する。
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数にGEMINI_API_KEYが設定されていません。")

    client = genai.Client(api_key=api_key)
    
    # Google Search機能を有効にしてモデルを初期化
    research_model = client.chats.create(
            model='gemini-2.0-flash-exp',
            config={'tools': [{'google_search': {}}]}
        )

    theme = topic_data['theme']
    keywords = ", ".join(topic_data['keywords'])

    # Geminiへの指示（プロンプト）
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
    try:
        response = research_model.send_message(prompt)
        return response.text
    except Exception as e:
        raise ConnectionError(f"Gemini APIとの通信中にエラーが発生しました: {e}")

def save_knowledge_as_json(file_path: str, data_to_add: dict):
    """生成された知識をJSONファイルに追記する。"""
    # 既存のデータを読み込む
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {"knowledge_entries": []}
    else:
        all_data = {"knowledge_entries": []}
    
    # 新しいデータを追加
    all_data["knowledge_entries"].append(data_to_add)
    
    # ファイルに書き戻す
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"知識データを {file_path} に保存しました。")
    
if __name__ == "__main__":
    JSON_FILE_PATH = "../data/clustered_output.json"
    OUTPUT_JSON_PATH = "../data/knowledge_base/knowledge_entries.json"

    try:
        # 1. JSONファイルからクラスタリング結果を読み込む
        clustered_data = load_json_file(JSON_FILE_PATH)
        
        if clustered_data and "clusters" in clustered_data:
            # 2. 複数のトピックからランダムに一つを選択
            selected_topic = random.choice(clustered_data["clusters"])
            
            print("--- 調査対象トピック ---")
            print(f"ID: {selected_topic['cluster_id']}")
            print(f"テーマ: {selected_topic['theme']}")
            print("------------------------\n")

            # 3. 選択したトピックについて調査・要約を実行
            summary_result = research_and_summarize_with_gemini(selected_topic)
            
            # 4. 結果を出力
            print("\n--- 調査・要約結果 ---")
            print(summary_result)
            print("----------------------\n")

            match = re.search(r"```json\s*(\{.*?\})\s*```", summary_result, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                data = json.loads(json_str) # 抽出したJSON文字列をパース

                tweet_text = data.get("tweet", "") # .get()で安全に取得
                if tweet_text:
                    print("--- 抽出されたツイート文 ---")
                    print(tweet_text)
                    print("--------------------------\n")

                knowledge_entry = {
                    "topic_id": selected_topic['cluster_id'],
                    "theme": selected_topic['theme'],
                    "keywords": selected_topic['keywords'],
                    "generated_tweet": tweet_text, # パースしたJSONデータをそのまま保存
                    "created_at": datetime.now().isoformat()
                }
                save_knowledge_as_json(OUTPUT_JSON_PATH, knowledge_entry)
            else:
                print("エラー: Geminiの応答からJSONデータを抽出できませんでした。")

    except (FileNotFoundError, ValueError, ConnectionError, json.JSONDecodeError) as e:
        print(f"エラーが発生しました: {e}")