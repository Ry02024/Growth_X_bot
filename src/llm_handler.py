# src/llm_handler.py
import json
import google.generativeai as genai
import config

# Gemini APIキーの設定
try:
    genai.configure(api_key=config.GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError("Failed to configure Gemini API. Check your GEMINI_API_KEY in the .env file.") from e


def cluster_knowledge(texts: list[str]) -> list[dict]:
    """
    Gemini APIを使用して知識群をクラスタリングし、テーマ名と要約を生成する。
    """
    if not texts:
        return []

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
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        cleaned_response_text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(cleaned_response_text)
    except Exception as e:
        print(f"Error during Gemini API call or JSON parsing: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Gemini response text: {response.text}")
        return []


def search_related_information(theme_name: str, theme_summary: str) -> list[str]:
    """
    関連情報を収集する（現在はダミー実装）。
    """
    print(f"Searching for information related to theme: {theme_name}")
    return [
        f"最新情報1: {theme_name}に関する新しい発見がありました。",
        f"関連ニュース: {theme_summary}についての議論が活発です。",
        f"ブログ記事: {theme_name}の応用例について解説します。"
    ]


def generate_tweet_text(theme_name: str, theme_summary: str, search_results: list[str]) -> str | None:
    """
    収集した情報とテーマを基に、X投稿用のツイート文を生成する。
    """
    search_info = "\n".join([f"- {res}" for res in search_results[:3]]) if search_results else "関連情報は現在見つかりませんでした。"

    prompt = f"""以下のテーマと関連情報に基づいて、X(旧Twitter)に投稿するための魅力的で簡潔なツイート文を1つ生成してください。
ツイートは最大でも130字程度に収めてください。ハッシュタグをいくつか含めてください。

テーマ名: {theme_name}
テーマ要約: {theme_summary}

関連情報:
{search_info}

ツイート文案:
"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during tweet generation with Gemini: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Gemini response text: {response.text}")
        return None