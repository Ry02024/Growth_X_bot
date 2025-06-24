# Growth_X_bot

## 概要

Growth_X_botは、Wordドキュメントなどの知識ベースから自動で情報を抽出・クラスタリングし、要約した内容をX（旧Twitter）へ自動投稿することで、知識共有や情報発信の効率化を図るためのBotです。

- Wordファイルからテキストを自動抽出
- クラスタリングによる情報整理
- クラスタごとにリサーチ・要約を自動生成
- 生成した要約をX（旧Twitter）に自動投稿

## 主な用途

- 社内ナレッジ、研究ノートなどの自動要約・SNS発信
- ドキュメントから新たな知見をアウトプットとして共有
- 定期的な情報発信・アウトプットの自動化

## ディレクトリ構成例

```
.
├── README.md
├── LICENSE
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── __pycache__/
│   ├── main.py
│   ├── cluster_document.py
│   ├── from_docx_import_Document.py
│   ├── research_topic.py
│   └── x_poster.py
├── data/
│   ├── knowledge_base/
│   │   └── 161217-master-Ryo.docx
│   ├── clustered_output.json
│   └── knowledge_entries.json
```

## セットアップ

### 1. 必要なライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. 必要なファイルの配置

- `data/knowledge_base/`フォルダ内に解析対象のWordファイル（例：161217-master-Ryo.docx）を配置してください。

### 3. X（Twitter）APIの設定

- 投稿にはX（Twitter）APIの認証情報が必要です。
- `python-dotenv`で`.env`ファイルを利用する場合は、各種キーを設定してください。

### 4. 実行方法

```bash
python src/main.py
```

## 依存パッケージ

- python-dotenv
- google-genai
- python-docx
- requests-oauthlib
- tweepy

## 注意事項

- Google Gemini APIやX（旧Twitter）APIの認証情報が必要です。各自取得し、環境変数または設定ファイルへセットしてください。
- 出力先パスやファイル名は適宜main.py内で変更してください。

## ライセンス

This project is licensed under the MIT License.

---

```
MIT License

Copyright (c) 2025 Ry02024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
