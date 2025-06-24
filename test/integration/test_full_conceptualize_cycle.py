# test/integration/test_full_conceptualize_cycle.py
import unittest
import os
import json
import sys

# パス設定
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

from src import main as bot_main # main.pyをbot_mainとしてインポート

class TestFullConceptualizeCycle(unittest.TestCase):

    def setUp(self):
        """テスト用のダミーファイルとパスを準備"""
        self.test_output_dir = os.path.join(project_root, 'test', 'test_outputs')
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # --- main.pyが参照するパスを、すべてテスト用の出力先に差し替える ---
        # 入力は本番データ、出力はテスト用ディレクトリ、と明確に分離する
        bot_main.KNOWLEDGE_ENTRIES_PATH = os.path.join(project_root, 'data', 'knowledge_base', 'knowledge_entries.json')
        bot_main.KNOWLEDGE_BASE_PATH = os.path.join(project_root, 'data', 'knowledge_base', '161217-master-Ryo.docx')
        
        # 出力先のパスをテスト専用ディレクトリに向ける
        bot_main.SUMMARY_MD_PATH = os.path.join(self.test_output_dir, 'test_summary.md') # MDファイルのパスを追加
        bot_main.HIGH_LEVEL_CONCEPTS_PATH = os.path.join(self.test_output_dir, 'test_high_concepts.json')
        bot_main.ACTIVITY_CLUSTERS_PATH = os.path.join(self.test_output_dir, 'test_activity_clusters.json')

    def test_run_conceptualize_cycle_directly(self):
        """
        mainモジュールの「run_conceptualize_cycle」関数が、
        MDファイルとJSONファイルの両方を正しく生成するかをテストする。
        """
        print("\n--- 統合テスト: 概念化サイクルを直接実行 ---")
        
        # 1. テスト対象の関数を実行
        bot_main.run_conceptualize_cycle()

        # --- 検証フェーズ ---
        # 検証1: 中間生成物（MDファイル）が正しく生成されたか
        self.assertTrue(os.path.exists(bot_main.SUMMARY_MD_PATH), "中間生成物（MDファイル）が作成されていません。")
        with open(bot_main.SUMMARY_MD_PATH, 'r', encoding='utf-8') as f:
            self.assertTrue(len(f.read()) > 50, "MDファイルの中身が短すぎます。")
        print("OK: 中間生成物（MDファイル）が正しく生成されました。")
        
        # 検証2: 高次概念ファイル（JSON）が正しく生成されたか
        self.assertTrue(os.path.exists(bot_main.HIGH_LEVEL_CONCEPTS_PATH), "高次概念ファイルが作成されていません。")
        print("OK: 高次概念ファイル（JSON）が正しく生成されました。")

        # 検証3: 最終的な活動クラスタファイル（JSON）が正しく生成されたか
        self.assertTrue(os.path.exists(bot_main.ACTIVITY_CLUSTERS_PATH), "活動クラスタファイルが作成されていません。")
        with open(bot_main.ACTIVITY_CLUSTERS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(len(data.get("clusters", [])), 5, "活動クラスタが5つ生成されていません。")
        print("OK: 活動クラスタファイルが正しく生成され、5つのクラスタが含まれています。")
        
        print("\nテスト成功: 概念化サイクルの全プロセスが正常に完了しました。")

    # def tearDown(self):
    #     """テストで生成された出力ファイルを削除"""
    #     for f_path in [
    #         bot_main.SUMMARY_MD_PATH,
    #         bot_main.HIGH_LEVEL_CONCEPTS_PATH,
    #         bot_main.ACTIVITY_CLUSTERS_PATH
    #     ]:
    #         if os.path.exists(f_path):
    #             os.remove(f_path)

if __name__ == '__main__':
    unittest.main()
