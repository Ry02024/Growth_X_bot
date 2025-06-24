# test/test_concept_generator.py
import os
import sys
import unittest
import json

# プロジェクトのルートディレクトリをシステムパスに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src import concept_generator

class TestConceptGenerator(unittest.TestCase):

    def setUp(self):
        """テストの前に毎回実行されるセットアップ処理"""
        # テスト用のファイルパスを整理して定義
        self.knowledge_file = os.path.join(project_root, 'data', 'knowledge_base', 'knowledge_entries.json')
        self.summary_file = os.path.join(project_root, 'data', 'knowledge_base', 'concept_summary_test.md')
        self.concept_file = os.path.join(project_root, 'data', 'knowledge_base', 'concepts_test_output.json')

        # 前回のテストで生成された可能性のあるファイルを確実に削除
        for f in [self.summary_file, self.concept_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_integration_generate_new_concept(self):
        """
        【統合テスト】知識入力→論説生成→JSON生成、という一連の流れが正しく動作するかを検証する。
        """
        print("\n--- 統合テスト: generate_new_concept を実行 ---")
        
        # 1. 本体となるメイン関数を実行
        concept_generator.generate_new_concept(self.knowledge_file, self.summary_file, self.concept_file)

        # 2. 中間生成物（論説ファイル）をより厳しくチェック
        self.assertTrue(os.path.exists(self.summary_file), "中間生成物（論説ファイル）が作成されていません。")
        with open(self.summary_file, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        self.assertTrue(len(summary_content.strip()) > 50, "論説ファイルの内容が極端に短いか、空です。")
        print("OK: 中間生成物（論説ファイル）が生成されました。")

        # 3. 最終生成物（JSONファイル）をより厳しくチェック
        self.assertTrue(os.path.exists(self.concept_file), "最終生成物（概念JSONファイル）が作成されていません。")
        with open(self.concept_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # conceptsキーなしの単一オブジェクト形式に対応
        self.assertIn("concept_name", data)
        self.assertIn("summary", data)
        self.assertIn("components", data)
        self.assertIn("implication", data)
        self.assertNotEqual(data["summary"].strip(), "", "JSONのsummaryが空です。")
        self.assertNotIn("No summary available.", data["summary"], "summaryが正しく生成されていません。")

        print("OK: 最終生成物（概念JSONファイル）が正しく生成され、内容も有効です。")
        print("\nテスト成功: 概念化の全プロセスが正常に完了しました。")

    # def tearDown(self):
    #     """テスト後に毎回実行されるクリーンアップ処理"""
    #     for f in [self.summary_file, self.concept_file]:
    #         if os.path.exists(f):
    #             os.remove(f)
    #             print(f"クリーンアップ: {f} を削除しました。")

if __name__ == '__main__':
    unittest.main()
