# src/utils.py
import json
import datetime
from pathlib import Path
import docx  # python-docxライブラリ


def load_knowledge_base(directory_path: str) -> list[str]:
    """
    指定されたディレクトリから知識ベースのテキストファイル (.txt) および
    Word文書ファイル (.docx) を読み込む。
    """
    texts = []
    knowledge_base_path = Path(directory_path)

    for file_path in knowledge_base_path.glob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                texts.append(f.read())
        except Exception as e:
            print(f"Error reading .txt file {file_path}: {e}")

    for file_path in knowledge_base_path.glob("*.docx"):
        try:
            doc = docx.Document(file_path)
            full_text = [para.text for para in doc.paragraphs]
            texts.append('\n'.join(full_text))
        except Exception as e:
            print(f"Error reading .docx file {file_path}: {e}")
    return texts


def save_clusters_to_json(clusters: list[dict], output_path: str):
    """
    クラスタリング結果をJSONファイルに保存する。
    """
    output_file_path = Path(output_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(clusters, f, ensure_ascii=False, indent=2)
        print(f"Clusters saved to {output_file_path}")
    except Exception as e:
        print(f"Error saving clusters to {output_file_path}: {e}")


def load_clusters(file_path: str) -> list[dict]:
    """
    クラスタ情報が保存されたJSONファイルを読み込む。
    """
    cluster_file = Path(file_path)
    if not cluster_file.is_file():
        return []
    try:
        with open(cluster_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {cluster_file}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading clusters: {e}")
        return []


def load_post_history(file_path: str) -> list[dict]:
    """
    投稿履歴ファイルを読み込む。
    """
    history_file = Path(file_path)
    if not history_file.is_file():
        return []
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # ファイルが空、または不正な形式の場合
        return []
    except Exception as e:
        print(f"Error loading post history: {e}")
        return []


def record_post_history(theme_name: str, tweet_text: str, post_id: str | None, history_file_path: str):
    """
    投稿履歴をJSONファイルに追記する。
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
    history_data = load_post_history(str(history_path))
    history_data.append(history_entry)
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    print(f"Post history updated in {history_path}")