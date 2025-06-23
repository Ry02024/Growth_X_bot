# config.py
import os
from dotenv import load_dotenv

# プロジェクトのルートディレクトリにある .env ファイルを読み込む
load_dotenv()

# --- API Keys (必須) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

# --- File Paths (任意、デフォルト値あり) ---
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
CLUSTERS_FILE = os.getenv("CLUSTERS_FILE", "data/clusters.json")
POST_HISTORY_FILE = os.getenv("POST_HISTORY_FILE", "data/post_history.json")

# --- Validation (推奨) ---
# 必須のキーが存在するかチェックし、なければエラーを発生させる
required_keys = [
    "GEMINI_API_KEY",
]
missing_keys = [key for key in required_keys if not globals()[key]]
if missing_keys:
    raise ValueError(f"Missing required environment variables in .env file: {', '.join(missing_keys)}")

# X関連のキーが一部でも設定されている場合は、すべて設定されているか確認する
x_key_map = {
    "X_API_KEY": X_API_KEY,
    "X_API_SECRET": X_API_SECRET,
    "X_ACCESS_TOKEN": X_ACCESS_TOKEN,
    "X_ACCESS_TOKEN_SECRET": X_ACCESS_TOKEN_SECRET,
}

x_key_values = x_key_map.values()
if any(x_key_values) and not all(x_key_values):
    missing_x_keys = [key for key, value in x_key_map.items() if not value]
    raise ValueError(
        "Some X API keys are set, but not all. "
        f"Please set all X keys or none of them. Missing: {', '.join(missing_x_keys)}"
    )
