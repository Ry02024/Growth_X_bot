# src/concept_generator.py
import os
import json
from dotenv import load_dotenv
from google import genai
import config

def _call_gemini(prompt: str) -> str:
    """Gemini APIを呼び出し、テキストを生成する共通関数 (research_topic.py方式)"""
    api_key = config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("環境変数にGEMINI_API_KEYが設定されていません。")
    client = genai.Client(api_key=api_key)
    # Gemini-proモデルでチャットを作成し、プロンプトを送信
    try:
        model = client.chats.create(model='gemini-2.0-flash-exp')
        response = model.send_message(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini APIとの通信中にエラーが発生しました: {e}")
        return ""

def create_summary_document(knowledge_text: str) -> str:
    """
    ツイート群から論文形式の要約テキストを生成（背景・目的・方法・結果・課題のフレームワーク）
    """
    prompt = f"""あなたは、複数の調査レポートから本質的な洞察を抽出し、学術的な視点で一つの概念を構築する優れた研究者です。

以下の複数のレポート群（日々の調査記録）を横断的に分析し、これら全てに共通する中心的な概念を見つけ出してください。
その概念について、**研究報告書の形式**で、必ず以下の構成で詳細に記述してください。

# 研究報告書：{{ここに抽出した概念を一言で表すタイトルを記述}}

## 1. 背景 (Background)
なぜ今、この概念が重要なのか。分析対象のレポート群から浮かび上がる社会的な文脈、技術的な動向、あるいは問題意識について説明してください。

## 2. 目的 (Objective)
この報告書が、この概念を分析することによって何を明らかにしようとしているのか、その目的を明確に定義してください。

## 3. 分析方法 (Methodology)
この概念を構成する要素をどのように特定したか。レポート群からどのような共通点やパターンを見つけ出し、どのように統合・分析したのか、そのプロセスを簡潔に説明してください。

## 4. 結果 (Results)
分析の結果、明らかになった「中心的な概念」の全体像を詳細に記述してください。この概念がどのような主要な要素から成り立っているのかを、箇条書きなどで分かりやすく示してください。
- **主要構成要素A**: (説明)
- **主要構成要素B**: (説明)
- ...

## 5. 考察と今後の課題 (Discussion & Future Issues)
この概念が持つ意味や重要性について考察し、さらに理解を深めるために今後どのような調査や議論が必要になるか、将来的な課題を提示してください。

---
【分析対象のレポート群】
{knowledge_text}
"""
    print("\n[Gemini] 論文形式の要約を生成中...")
    summary = _call_gemini(prompt)
    return summary

def structure_document_to_json(summary_document: str) -> dict:
    """
    論文テキストを構造化JSONに変換
    """
    prompt = f"""あなたは、与えられた研究報告書を分析し、指定されたJSON形式に正確に変換するデータサイエンティストです。
以下の研究報告書を読み、その内容を下記のJSONフォーマットに厳密に従って変換してください。

【JSONフォーマット】
{{
  "concept_name": "（報告書のタイトル）",
  "summary": "（「結果」セクションの要約）",
  "components": ["（「結果」で示された主要構成要素のリスト）"],
  "implication": "（「考察と今後の課題」セクションの要約）"
}}

---
【変換対象の研究報告書】
{summary_document}
"""
    print("[Gemini] 論文をJSON形式に変換中...")
    json_str = _call_gemini(prompt)
    try:
        clean_json_str = json_str.strip().lstrip("```json").rstrip("```")
        return json.loads(clean_json_str)
    except json.JSONDecodeError:
        print("エラー: Geminiからの出力が有効なJSON形式ではありません。")
        return {}

def generate_new_concept(knowledge_file: str, summary_file: str, concept_file: str) -> dict:
    """
    knowledge_file: 入力となるknowledge_entries.jsonのパス
    summary_file: 中間生成物（論文形式テキスト）のパス
    concept_file: 出力するconcepts.jsonのパス
    戻り値: 生成された概念データ（辞書）
    """
    with open(knowledge_file, 'r', encoding='utf-8') as f:
        knowledge_data = json.load(f)
    entries = knowledge_data.get('knowledge_entries', [])
    knowledge_text = "\n".join([
        f"テーマ: {e.get('theme', '')}\nツイート: {e.get('generated_tweet', '')}\n詳細: {e.get('details', '')}"
        for e in entries
    ])
    summary_document = create_summary_document(knowledge_text)
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_document)
    concepts_json = structure_document_to_json(summary_document)
    with open(concept_file, 'w', encoding='utf-8') as f:
        json.dump(concepts_json, f, ensure_ascii=False, indent=2)
    # 生成したJSONデータを返す
    return concepts_json
