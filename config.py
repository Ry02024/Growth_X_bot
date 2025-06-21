# config.py
import os
from dotenv import load_dotenv

# プロジェクトのルートディレクトリにある .env ファイルを読み込む
load_dotenv()

# --- API Keys (必須) ---
# .envファイルにこれらのキーを設定してください
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_KEY_SECRET = os.getenv("X_API_KEY_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

# --- File Paths (任意、デフォルト値あり) ---
# .envで上書き可能
# プロジェクトのルートからの相対パス
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
CLUSTERS_FILE = os.getenv("CLUSTERS_FILE", "data/clusters.json")
POST_HISTORY_FILE = os.getenv("POST_HISTORY_FILE", "data/post_history.json")

# --- Validation (推奨) ---
# 必須のキーが存在するかチェックし、なければエラーを発生させる
# Xへの投稿を有効にする場合は、X関連のキーも.envファイルに設定してください。
required_keys = [
    "GEMINI_API_KEY",
]
missing_keys = [key for key in required_keys if not globals()[key]]
if missing_keys:
    raise ValueError(f"Missing required environment variables in .env file: {', '.join(missing_keys)}")

# X関連のキーが一部でも設定されている場合は、すべて設定されているか確認する
x_keys = [X_API_KEY, X_API_KEY_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]
if any(x_keys) and not all(x_keys):
    missing_x_key_names = [
        name for name, value in {
            "X_API_KEY": X_API_KEY,
            "X_API_KEY_SECRET": X_API_KEY_SECRET,
            "X_ACCESS_TOKEN": X_ACCESS_TOKEN,
            "X_ACCESS_TOKEN_SECRET": X_ACCESS_TOKEN_SECRET
        }.items() if not value
    ]
    raise ValueError(
        f"Some X API keys are set, but not all. Please set all X keys or none of them. Missing: {', '.join(missing_x_key_names)}"
    )