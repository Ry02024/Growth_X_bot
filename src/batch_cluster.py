# batch_cluster.py
# 知識クラスタリング機能の実装予定

import os
import json
import google.generativeai as genai
from pathlib import Path
import config # config.pyをインポート

# Gemini APIキーの設定
genai.configure(api_key=config.GEMINI_API_KEY)

def load_knowledge_base(directory_path: str) -> list[str]:
    """
    指定されたディレクトリから知識ベースのテキストファイルを読み込む。
    """
    texts = []
    knowledge_base_path = Path(directory_path)
    for file_path in knowledge_base_path.glob("*.txt"): # .txtファイルのみを対象とする例
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                texts.append(f.read())
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    return texts

def cluster_knowledge(texts: list[str]) -> list[dict]:
    """
    Gemini APIを使用して知識群をクラスタリングし、テーマ名と要約を生成する。
    """
    if not texts:
        return []

    # プロンプトの例 (実際のプロンプトはより詳細な指示が必要)
    combined_text = "\n---\n".join(texts)
    prompt = f"""以下の知識群をKJ法的なアプローチで分析し、複数の意味的なクラスタに分類してください。
各クラスタについて、以下の情報を抽出してください。
1. クラスタのテーマ名（簡潔で分かりやすい名前）
2. クラスタの要約（クラスタ全体の内容を代表する数文程度の説明）

出力はJSON形式で、各クラスタを要素とするリストとしてください。
例:
[
  {{
    "theme_name": "テーマA",
    "summary": "テーマAに関する要約文です。"
  }},
  {{
    "theme_name": "テーマB",
    "summary": "テーマBに関する要約文です。"
  }}
]

知識群:
{combined_text}
"""

    try:
        model = genai.GenerativeModel('gemini-pro') # モデル名は適宜変更
        response = model.generate_content(prompt)
        
        cleaned_response_text = response.text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
        
        clusters = json.loads(cleaned_response_text)
        return clusters
    except Exception as e:
        print(f"Error during Gemini API call or JSON parsing: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Gemini response text: {response.text}")
        return []


def save_clusters_to_json(clusters: list[dict], output_path: str):
    """
    クラスタリング結果をJSONファイルに保存する。
    """
    output_file_path = Path(output_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True) # ディレクトリがなければ作成
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(clusters, f, ensure_ascii=False, indent=2)
        print(f"Clusters saved to {output_file_path}")
    except Exception as e:
        print(f"Error saving clusters to {output_file_path}: {e}")

if __name__ == '__main__':
    print("Starting knowledge clustering process...")
    
    knowledge_dir = config.KNOWLEDGE_BASE_DIR
    clusters_output_file = config.CLUSTERS_FILE

    knowledge_texts = load_knowledge_base(knowledge_dir)
    if not knowledge_texts:
        print(f"No knowledge base files found in {knowledge_dir} or an error occurred.")
    else:
        print(f"Loaded {len(knowledge_texts)} documents from knowledge base.")
        generated_clusters = cluster_knowledge(knowledge_texts)
        
        if generated_clusters:
            save_clusters_to_json(generated_clusters, clusters_output_file)
            print("Knowledge clustering process finished.")
        else:
            print("No clusters were generated.")
