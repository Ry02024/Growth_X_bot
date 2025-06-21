# src/cluster_generator.py
from pathlib import Path
import config
from src import utils, llm_handler

def generate_clusters_if_needed(force_recluster: bool = False) -> bool:
    """
    クラスタファイルが存在しない場合、または強制実行が指定された場合にクラスタリング処理を実行する。
    成功または処理不要の場合は True を、失敗した場合は False を返す。
    """
    clusters_file = Path(config.CLUSTERS_FILE)
    if force_recluster or not clusters_file.is_file() or clusters_file.stat().st_size == 0:
        if force_recluster:
            print("Force re-clustering as requested...")
        else:
            print(f"Cluster file '{config.CLUSTERS_FILE}' not found or empty. Running clustering...")

        knowledge_texts = utils.load_knowledge_base(config.KNOWLEDGE_BASE_DIR)
        if not knowledge_texts:
            print(f"No knowledge base files found in '{config.KNOWLEDGE_BASE_DIR}'. Cannot create clusters.")
            return False

        print(f"Loaded {len(knowledge_texts)} documents. Generating clusters with Gemini...")
        generated_clusters = llm_handler.cluster_knowledge(knowledge_texts)

        if generated_clusters:
            utils.save_clusters_to_json(generated_clusters, config.CLUSTERS_FILE)
            print("Knowledge clustering process finished.")
            return True
        else:
            print("No clusters were generated. Halting process.")
            return False
    # クラスタリングが不要だった場合
    return True