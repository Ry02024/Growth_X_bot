# test/integration/test_main.py
import unittest
import os
import json
import sys
from unittest.mock import patch

# パス設定
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
from src import main as bot_main

class TestMainLifecycle(unittest.TestCase):
    def setUp(self):
        self.test_output_dir = os.path.join(project_root, 'test', 'test_outputs')
        os.makedirs(self.test_output_dir, exist_ok=True)
        # main.pyが参照するパスを、すべてテスト用の出力先に差し替える
        bot_main.KNOWLEDGE_BASE_PATH = os.path.join(project_root, 'data', 'knowledge_base', '161217-master-Ryo.docx')
        bot_main.KNOWLEDGE_ENTRIES_PATH = os.path.join(self.test_output_dir, 'test_knowledge_entries.json')
        bot_main.SUMMARY_MD_PATH = os.path.join(self.test_output_dir, 'test_summary.md')
        bot_main.HIGH_LEVEL_CONCEPTS_PATH = os.path.join(self.test_output_dir, 'test_high_concepts.json')
        bot_main.ACTIVITY_CLUSTERS_PATH = os.path.join(self.test_output_dir, 'test_activity_clusters.json')
        # main.pyの設定値をテスト用に差し替える
        self.original_threshold = bot_main.CONCEPT_GENERATION_THRESHOLD
        bot_main.CONCEPT_GENERATION_THRESHOLD = 2 # テスト用に2回で概念化
        # テスト開始前に出力ファイルをすべて削除
        # for f in [bot_main.KNOWLEDGE_ENTRIES_PATH, bot_main.SUMMARY_MD_PATH, bot_main.HIGH_LEVEL_CONCEPTS_PATH, bot_main.ACTIVITY_CLUSTERS_PATH]:
        #     if os.path.exists(f): os.remove(f)

    @patch('src.x_poster.post_to_x')
    @patch('time.sleep') # time.sleepも無効化してテストを高速化
    def test_full_bot_lifecycle(self, mock_sleep, mock_post_to_x):
        """通常サイクル→概念化サイクルという一連のライフサイクルをテスト"""
        print("\n--- ライフサイクル統合テスト開始 ---")
        # 柔軟なテスト: 短期記憶の件数に応じて期待値を計算
        try:
            with open(bot_main.RECENT_KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
                before = len(json.load(f).get("knowledge_entries", []))
        except (FileNotFoundError, json.JSONDecodeError, AttributeError):
            before = 0
        bot_main.main()
        # 検証
        self.assertTrue(os.path.exists(bot_main.ACTIVITY_CLUSTERS_PATH), "活動クラスタファイルが生成されていません。")
        self.assertTrue(os.path.exists(bot_main.HIGH_LEVEL_CONCEPTS_PATH), "高次概念ファイルが生成されていません。")
        # 概念化後は短期記憶がリセットされていること
        try:
            with open(bot_main.RECENT_KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
                after = len(json.load(f).get("knowledge_entries", []))
        except (FileNotFoundError, json.JSONDecodeError, AttributeError):
            after = 0
        self.assertEqual(after, 0, "概念化後に短期記憶がリセットされていません。")
        # 投稿回数は閾値-beforeまたは0
        expected_posts = max(0, bot_main.CONCEPT_GENERATION_THRESHOLD - before)
        self.assertEqual(mock_post_to_x.call_count, expected_posts, f"通常サイクルが{expected_posts}回実行されていません。")
        print(f"テスト成功: {expected_posts}回投稿→概念化→終了、のサイクルが確認できました。")

    def tearDown(self):
        bot_main.CONCEPT_GENERATION_THRESHOLD = self.original_threshold # 設定値を元に戻す

if __name__ == '__main__':
    unittest.main()