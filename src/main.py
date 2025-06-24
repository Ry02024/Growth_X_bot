# src/main.py
import os
import sys
import json
import random
import re
from datetime import datetime

# --- モジュール検索パスの設定 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# --- 各機能モジュールのインポート ---
from src import from_docx_import_Document, cluster_document, research_topic, x_poster, concept_generator

# --- グローバル設定値 ---
CONCEPT_GENERATION_THRESHOLD = 10

# --- ファイルパス定義 ---
KNOWLEDGE_BASE_PATH = os.path.join(project_root, 'data', 'knowledge_base', '161217-master-Ryo.docx')
KNOWLEDGE_ENTRIES_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'knowledge_entries.json')
HIGH_LEVEL_CONCEPTS_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'high_level_concepts.json')
ACTIVITY_CLUSTERS_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'activity_clusters.json')
SUMMARY_MD_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'concept_summary.md')

# --- 関数定義 ---
def get_current_post_count() -> int:
    # (この関数は変更なし)
    try:
        with open(KNOWLEDGE_ENTRIES_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return len(data.get("knowledge_entries", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def run_normal_cycle():
    """【通常サイクル】既存の活動クラスタからツイートを生成・投稿する。"""
    print("\n--- 通常サイクルを実行します ---")
    print(f"[DEBUG] KNOWLEDGE_ENTRIES_PATH: {KNOWLEDGE_ENTRIES_PATH}")
    
    try:
        with open(ACTIVITY_CLUSTERS_PATH, 'r', encoding='utf-8') as f:
            clustered_data = json.load(f)
    except FileNotFoundError:
        print(f"エラー: 活動計画ファイル({ACTIVITY_CLUSTERS_PATH})が見つかりません。"); print("初回実行として、先に概念化サイクルを強制実行します。"); run_conceptualize_cycle(); return

    selected_topic = random.choice(clustered_data["clusters"])
    print(f"調査対象テーマ: {selected_topic['theme']}")
    
    research_result_text = research_topic.research_and_summarize_with_gemini(selected_topic)
    print(f"[DEBUG] research_result_text: {research_result_text}")
    
    match = re.search(r"\{.*\}", research_result_text, re.DOTALL)
    if not match:
        print("エラー: 調査結果からJSONを抽出できませんでした。")
        return
        
    research_json_data = json.loads(match.group(0))
    tweet_text = research_json_data.get("tweet", "")
    print(f"[DEBUG] tweet_text: {tweet_text}")
    
    if tweet_text:
        # 知識記録のエントリを作成
        knowledge_entry = {
            "topic_id": selected_topic.get('cluster_id', 'N/A'),
            "theme": selected_topic.get('theme', 'N/A'),
            "keywords": selected_topic.get('keywords', []),
            "generated_tweet": tweet_text,
            "full_research": research_json_data,
            "created_at": datetime.now().isoformat()
        }

        # 知識記録ファイルに追記保存
        try:
            with open(KNOWLEDGE_ENTRIES_PATH, 'r', encoding='utf-8') as f:
                all_entries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_entries = {"knowledge_entries": []}
        # 新しいエントリを追加
        print(f"知識記録の場所: {KNOWLEDGE_ENTRIES_PATH}")
        print(f"新しい知識記録を追加: {all_entries}")
        all_entries["knowledge_entries"].append(knowledge_entry)

        with open(KNOWLEDGE_ENTRIES_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_entries, f, ensure_ascii=False, indent=2)
        print(f"新しい知識記録を {KNOWLEDGE_ENTRIES_PATH} に保存しました。")

        # Xに投稿
        x_poster.post_to_x(tweet_text)
    else:
        print("警告: 調査結果からツイート文が生成されませんでした。投稿をスキップします。")
        
    print("通常サイクルを完了しました。")


def run_conceptualize_cycle():
    """【概念化サイクル】高次概念の生成と、活動クラスタの再分類を行う。"""
    print(f"\n--- 概念化サイクルを実行します ---")
    
    # ステップA: 高次概念の生成と保存
    print("ステップA: 新しい高次概念を生成しています...")
    # generate_new_conceptを使い、MDとJSONを生成
    new_concept_data = concept_generator.generate_new_concept(
        KNOWLEDGE_ENTRIES_PATH,
        SUMMARY_MD_PATH,
        HIGH_LEVEL_CONCEPTS_PATH
    )
    
    # ステップC & D: 全知識の統合と再クラスタリング
    print("ステップC&D: 全知識を統合し、新しい活動クラスタを生成しています...")
    knowledge_text = from_docx_import_Document.get_combined_knowledge_text(KNOWLEDGE_BASE_PATH, HIGH_LEVEL_CONCEPTS_PATH)
    new_clusters_json_text = cluster_document.get_clustered_json_from_gemini(knowledge_text)
    json_str = new_clusters_json_text.strip().lstrip("```json").rstrip("```")
    new_clusters_data = json.loads(json_str)
    with open(ACTIVITY_CLUSTERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_clusters_data, f, ensure_ascii=False, indent=2)
    print(f"新しい活動クラスタを {ACTIVITY_CLUSTERS_PATH} に保存しました。")


# --- ▼▼▼ プログラムの実行開始地点 ▼▼▼ ---
def main():
    """このボットのメインコントローラー"""
    print(f"======== ボット処理開始 ({datetime.now()}) ========")
    
    post_count = get_current_post_count()
    print(f"現在の投稿数: {post_count}")

    if post_count >= CONCEPT_GENERATION_THRESHOLD:
        run_conceptualize_cycle()
    else:
        run_normal_cycle()
        
    print(f"======== 今回の処理完了 ({datetime.now()}) ========\n")

# このファイルが直接実行された時だけmain()を呼び出す
if __name__ == "__main__":
    main()