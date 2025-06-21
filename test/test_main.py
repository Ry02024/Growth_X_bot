import from_docx_import_Document
import test_cluster_document
import test_research_topic
import test_x_poster
import json, re, os, random, sys, requests
from datetime import datetime

#まずはドキュメントからテキストを読み込む
knowledge_base_path = "../data/knowledge_base/161217-master-Ryo.docx"
read_test = from_docx_import_Document.read_first_text_in_docx(knowledge_base_path)
# 次にクラスタリングを実行
clustered_output_path = "../data/clustered_output.json"
result = test_cluster_document.get_clustered_json_from_gemini(read_test)
#テストで出力されたクラスタリング結果を確認
print("クラスタリング結果:")
print(result)
# 最後に調査と要約を実行
research_topic_path = "../data/knowledge_base/knowledge_entries.json"
clustered_data = test_research_topic.load_json_file(clustered_output_path)
import random
selected_topic = random.choice(clustered_data["clusters"])
research_result = test_research_topic.research_and_summarize_with_gemini(selected_topic)
# 調査結果を確認
print("調査と要約の結果:")
print(research_result)
# 調査結果をJSONファイルに保存
match = re.search(r"```json\s*(\{.*?\})\s*```", research_result, re.DOTALL)
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
test_research_topic.save_knowledge_as_json(research_topic_path, knowledge_entry)
# test_research_topic.save_research_result_to_json(research_result, "../data/research_results.json")
# 調査結果の保存を確認
print("調査結果が保存されました。")
# 投稿モジュールをテスト
latest_tweet = test_x_poster.get_latest_tweet(research_topic_path)

# 2. ツイート文を140字以内に調整
trimmed_tweet = test_x_poster.trim_to_140_chars(latest_tweet)

# 3. Xに投稿
test_x_poster.post_to_x(trimmed_tweet)