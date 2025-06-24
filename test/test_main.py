import sys
import os
# プロジェクトルートから実行する前提でsrcとtestをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.dirname(__file__))

import from_docx_import_Document
import test_cluster_document
import test_research_topic
import test_x_poster
import json, re, random
from datetime import datetime

KNOWLEDGE_BASE_PATH = "data/knowledge_base/161217-master-Ryo.docx"
CONCEPTS_PATH = "data/knowledge_base/concepts_test_output.json"

# ▼▼▼ 安全な切り替えスイッチ ▼▼▼
if os.path.exists(CONCEPTS_PATH):
    print("新しい概念ファイルが見つかりました。知識を統合します。")
    read_test = from_docx_import_Document.get_combined_knowledge_text(KNOWLEDGE_BASE_PATH, CONCEPTS_PATH)
else:
    print("基本知識ベースのみ使用します。")
    read_test = from_docx_import_Document.read_first_text_in_docx(KNOWLEDGE_BASE_PATH)
# ▲▲▲ 切り替えここまで ▲▲▲

clustered_output_path = "data/clustered_output.json"
result = test_cluster_document.get_clustered_json_from_gemini(read_test)
print("クラスタリング結果:")
print(result)
research_topic_path = "data/knowledge_base/knowledge_entries.json"
clustered_data = test_research_topic.load_json_file(clustered_output_path)
selected_topic = random.choice(clustered_data["clusters"])
research_result = test_research_topic.research_and_summarize_with_gemini(selected_topic)
print("調査と要約の結果:")
print(research_result)
match = re.search(r"```json\s*(\{.*?\})\s*```", research_result, re.DOTALL)
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
test_research_topic.save_knowledge_as_json(research_topic_path, knowledge_entry)
print("調査結果が保存されました。")
latest_tweet = test_x_poster.get_latest_tweet(research_topic_path)
trimmed_tweet = test_x_poster.trim_to_140_chars(latest_tweet)
test_x_poster.post_to_x(trimmed_tweet)