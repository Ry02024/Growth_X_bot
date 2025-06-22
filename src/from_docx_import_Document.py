# src/from_docx_import_Document.py
from docx import Document
import os

def read_first_text_in_docx(file_path):
    """
    docxファイルを読み込み、最初に見つかったテキストを含む段落から100文字を出力する。
    """
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません - {file_path}")
        return
    try:
        document = Document(file_path)
        
        # テキストを含む最初の段落を探す
        for paragraph in document.paragraphs:
            # .strip()で空白や改行のみの段落を無視する
            if paragraph.text.strip():
                print("最初に見つかったテキスト:")
                print(paragraph.text[:100])
                return # テキストを見つけたら処理を終了

        print("ドキュメント内にテキストを含む段落が見つかりませんでした。")
        print("原因の可能性: 1. 全て空行である 2. テキストが段落ではなくテキストボックス等に含まれている")

    except Exception as e:
        print(f"ファイルの読み込み中にエラーが発生しました: {e}")

if __name__ == "__main__":
    # ご自身のファイルパスに修正してください
    file_path = "../data/knowledge_base/161217-master-Ryo.docx"
    read_first_text_in_docx(file_path)