#test/integration/test_normal_cycle.py
import unittest
import os
import json
import sys

# パス設定
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

# テスト対象のモジュールをインポート
from src import main as bot_main
from unittest.mock import patch # Xへの実際の投稿を防ぐために使用

class TestNormalCycle(unittest.TestCase):

    def setUp(self):
        """テストの準備：入力ファイルと出力先のパスを設定する"""
        self.test_output_dir = os.path.join(project_root, 'test', 'test_outputs')
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # --- main.pyが参照するパスを、テスト用のパスに差し替える ---
        
        # ★★★ 入力ファイル ★★★
        # 概念化テストで生成されたファイルを指定
        bot_main.ACTIVITY_CLUSTERS_PATH = os.path.join(self.test_output_dir, 'test_activity_clusters.json')
        # 新しい記憶ファイルのパスをテスト用に差し替え
        bot_main.RECENT_KNOWLEDGE_PATH = os.path.join(self.test_output_dir, 'test_recent_knowledge.json')
        bot_main.ALL_KNOWLEDGE_LOG_PATH = os.path.join(self.test_output_dir, 'test_all_knowledge_log.json')
        
        # ★★★ 出力ファイル ★★★
        # 通常サイクルの結果（知識記録）の保存先
        bot_main.KNOWLEDGE_ENTRIES_PATH = os.path.join(self.test_output_dir, 'test_knowledge_entries.json')

        # --- テストの前提条件をチェック ---
        # 入力ファイルが存在しないとテストが始まらないので、ここで確認
        self.assertTrue(
            os.path.exists(bot_main.ACTIVITY_CLUSTERS_PATH),
            f"テストの前提エラー: 入力ファイル {bot_main.ACTIVITY_CLUSTERS_PATH} が存在しません。\n"
            "先に test_full_conceptualize_cycle を実行してください。"
        )
        
        # # 出力ファイルは、テスト開始前に空の状態にしておく
        # if os.path.exists(bot_main.KNOWLEDGE_ENTRIES_PATH):
        #     os.remove(bot_main.KNOWLEDGE_ENTRIES_PATH)


    # X投稿をモック化（無効化）してテストを実行
    @patch('src.x_poster.post_to_x')
    def test_run_normal_cycle_successfully(self, mock_post_to_x):
        """
        【統合テスト】通常サイクルが、ツイート生成→知識記録→投稿関数呼び出し、を正しく行うか
        """
        print("\n--- 統合テスト: 通常サイクルを直接実行 ---")
        
        # テスト開始前のエントリ数を記録
        try:
            with open(bot_main.RECENT_KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
                before = len(json.load(f).get("knowledge_entries", []))
        except (FileNotFoundError, json.JSONDecodeError):
            before = 0

        # テスト対象の関数を実行
        bot_main.run_normal_cycle()
        
        # --- 検証フェーズ ---
        # 検証: 短期記憶ファイルに1件追加されたか
        with open(bot_main.RECENT_KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
            after = len(json.load(f).get("knowledge_entries", []))
        self.assertEqual(after, before + 1, "知識エントリが1件追加されていません。")
        print(f"OK: 短期記憶エントリが{before}→{after}件になりました。")
        
        # 検証3: X投稿関数が1回呼び出されたか
        mock_post_to_x.assert_called_once()
        print("OK: X投稿関数が1回呼び出されました。（実際の投稿はしていません）")


    def tearDown(self):
        # """テスト後に生成された出力ファイルを削除"""
        # # このテストで生成されたtest_knowledge_entries.jsonのみ削除する
        # # 入力として使ったtest_activity_clusters.jsonは消さない
        # if os.path.exists(bot_main.KNOWLEDGE_ENTRIES_PATH):
        #     os.remove(bot_main.KNOWLEDGE_ENTRIES_PATH)
        pass

if __name__ == '__main__':
    unittest.main()