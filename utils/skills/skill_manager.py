#!/usr/bin/env python3
import os
import hashlib
from typing import List, Dict, Any 

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, 
    FieldCondition, MatchValue, MatchAny, 
    TextIndexParams, TextIndexType, TokenizerType
)
from flashrank import Ranker, RerankRequest
from utils.core.config_loader import get_qdrant_host, get_qdrant_port, get_enable_skills, get_project_hash
from utils.core.translator import t
from utils.core.config_loader import get_qdrant_host, get_qdrant_port, get_enable_skills
import socket
import sys
from utils.themes.styles import LOGS

# Constantes de rutas
ANTFLOW_HOME_DIR = os.path.expanduser("~/.antflow")
LOCAL_MODELS_DIR = os.path.join(ANTFLOW_HOME_DIR, "local_models")


def ensure_antflow_directories():
    """Asegura que existan los directorios necesarios en ~/.antflow"""
    os.makedirs(ANTFLOW_HOME_DIR, exist_ok=True)
    os.makedirs(LOCAL_MODELS_DIR, exist_ok=True)


def load_transformer_model(model_id):
    import os
    from contextlib import redirect_stdout, redirect_stderr
    from io import StringIO

    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '0'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

    from sentence_transformers import SentenceTransformer
    from huggingface_hub import snapshot_download
    import torch
    import transformers

    transformers.logging.set_verbosity_error()
    transformers.logging.disable_progress_bar()

    ensure_antflow_directories()

    model_name_flat = model_id.split('/')[-1]
    base_path = os.path.join(LOCAL_MODELS_DIR, model_name_flat)

    if not os.path.exists(base_path):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            snapshot_download(
                repo_id=model_id,
                local_dir=base_path,
                ignore_patterns=["*.onnx", "*.ot", "*.h5", "openvino*", "*.msgpack"],
                resume_download=True,
            )

    device = "cpu"
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"

    if os.path.exists(os.path.join(base_path, "config.json")):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            return SentenceTransformer(base_path, device=device)
    else:
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            return SentenceTransformer(model_id, device=device)


def load_ranker_model(model_id):
    import os
    from contextlib import redirect_stdout, redirect_stderr
    from io import StringIO

    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

    from flashrank import Ranker

    ensure_antflow_directories()

    model_name_flat = model_id.split('/')[-1]
    cache_dir = os.path.join(LOCAL_MODELS_DIR, f"flashrank_{model_name_flat}")

    try:
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            ranker = Ranker(model_name=model_id, cache_dir=cache_dir)
        return ranker
    except Exception as e:
        raise RuntimeError(t("error_downloading_ranker").format(error=e)) from e


def verify_qdrant_connection():
    """Verifica si la conexión a Qdrant es válida"""
    if not get_enable_skills():
        return True, t("qdrant_skills_disabled")

    host = get_qdrant_host()
    port = get_qdrant_port()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()

        if result != 0:
            return False, t("qdrant_connection_error").format(host=host, port=port)

        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from qdrant_client import QdrantClient
            client = QdrantClient(host=host, port=port, prefer_grpc=False, check_compatibility=False)

            try:
                client.get_collections()
                return True, t("qdrant_connection_success").format(host=host, port=port)
            except Exception as e:
                return False, t("qdrant_server_error").format(error=str(e))

    except socket.timeout:
        return False, t("qdrant_timeout_error").format(host=host, port=port)
    except Exception as e:
        return False, t("qdrant_unexpected_error").format(error=str(e), host=host, port=port)


class SkillManager:
    def __init__(self):
        from utils.core.logg.ui_logger import get_ui_logger
        self.ui_logger = get_ui_logger()

        if not get_enable_skills():
            self.enabled = False
            return

        self.enabled = True
        self.project_hash = get_project_hash()
        self.collection_name = f"skills_{self.project_hash}"

        try:
            HOST = get_qdrant_host()
            PORT = get_qdrant_port()
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.q_client = QdrantClient(host=HOST, port=PORT, prefer_grpc=False, check_compatibility=False)
        except Exception as e:
            self.ui_logger.append(t("qdrant_connection_error").format(error=e), LOGS.error)
            self.q_client = None

        self.embedding_model = None
        self.ranker = None
        self._models_loaded = False

        from langchain_text_splitters import RecursiveCharacterTextSplitter
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)

        if self.q_client:
            self._init_collection()

    def _load_models_if_needed(self):
        """Carga los modelos de forma lazy cuando se necesitan por primera vez."""
        if self._models_loaded:
            return

        try:
            self.ui_logger.append("Loading embedding model...", LOGS.info)
            self.embedding_model = load_transformer_model('sentence-transformers/all-MiniLM-L6-v2')

            try:
                self.ui_logger.append("Loading ranker model...", LOGS.info)
                self.ranker = load_ranker_model("ms-marco-MiniLM-L-12-v2")
                self.ui_logger.append("Models loaded successfully", LOGS.success)
            except Exception as e:
                self.ui_logger.append(t("flashrank_warning").format(error=e), LOGS.warning)
                self.ranker = None

            self._models_loaded = True

        except Exception as e:
            self.ui_logger.append(f"Error loading models: {e}", LOGS.error)
            self.embedding_model = None
            self.ranker = None
            self._models_loaded = False

    def _init_collection(self):
        try:
            cols = self.q_client.get_collections().collections
            if not any(c.name == self.collection_name for c in cols):
                self.q_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
                self.q_client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="text",
                    field_schema=TextIndexParams(
                        type=TextIndexType.TEXT,
                        tokenizer=TokenizerType.MULTILINGUAL,
                        lowercase=True,
                    )
                )
        except Exception as e:
            self.ui_logger.append(f"Error init: {e}", LOGS.error)

    def skill_ingest(self, file_path: str, skill_name: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"success": False, "error": "Skills deshabilitadas"}
        if not os.path.exists(file_path):
            return {"success": False, "error": "No file"}

        self._load_models_if_needed()
        if not self.embedding_model:
            return {"success": False, "error": "Embedding model not available"}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        chunks = self.text_splitter.split_text(content)
        points = []

        for i, chunk in enumerate(chunks):
            v = self.embedding_model.encode(chunk, show_progress_bar=False).tolist()
            p_id = int(hashlib.md5(f"{skill_name}_{i}".encode()).hexdigest(), 16) % (2**32)
            points.append(PointStruct(
                id=p_id, vector=v,
                payload={"text": chunk, "skill_id": skill_name, "enabled": True}
            ))

        self.q_client.upsert(collection_name=self.collection_name, points=points)
        return {"success": True}

    def search_skills(self, query: str, active_skills_ids: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []

        self._load_models_if_needed()
        if not self.embedding_model:
            return []

        try:
            v = self.embedding_model.encode(query, show_progress_bar=False).tolist()
            hits = self.q_client.query_points(
                collection_name=self.collection_name,
                query=v,
                query_filter=Filter(
                    must=[
                        FieldCondition(key="enabled", match=MatchValue(value=True)),
                        FieldCondition(key="skill_id", match=MatchAny(any=active_skills_ids))
                    ]
                ),
                limit=top_k * 3,
                with_payload=True
            ).points

            if not hits:
                return []

            if not self.ranker:
                return [{"text": h.payload["text"], "score": h.score, "skill": h.payload["skill_id"]} for h in hits[:top_k]]

            passages = [{"id": h.id, "text": h.payload["text"], "meta": {"skill": h.payload["skill_id"]}} for h in hits]
            rerank_request = RerankRequest(query=query, passages=passages)
            results = self.ranker.rerank(rerank_request)

            return [{"text": r["text"], "score": r["score"], "skill": r["meta"]["skill"]} for r in results[:top_k]]

        except Exception as e:
            self.ui_logger.append(t("search_error").format(error=e), LOGS.error)
            return []

    def set_skill_enabled(self, skill_id: str, enabled: bool) -> bool:
        if not self.enabled:
            return False

        try:
            filter_by_skill = Filter(
                must=[FieldCondition(key="skill_id", match=MatchValue(value=skill_id))]
            )

            points, _ = self.q_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_by_skill,
                limit=1000,
                with_payload=True,
                with_vectors=True
            )

            if not points:
                self.ui_logger.append(t("no_points_found").format(skill_id=skill_id), LOGS.warning)
                return False

            updated_points = []
            for point in points:
                if point.vector is not None:
                    updated_points.append(PointStruct(
                        id=point.id,
                        vector=point.vector,
                        payload={**point.payload, "enabled": enabled}
                    ))
                else:
                    self.ui_logger.append(t("regenerating_vector").format(point_id=point.id), LOGS.warning)
                    self._load_models_if_needed()
                    if not self.embedding_model:
                        continue
                    vector = self.embedding_model.encode(point.payload["text"]).tolist()
                    updated_points.append(PointStruct(
                        id=point.id,
                        vector=vector,
                        payload={**point.payload, "enabled": enabled}
                    ))

            if updated_points:
                self.q_client.upsert(
                    collection_name=self.collection_name,
                    points=updated_points
                )
                status = "habilitada" if enabled else "deshabilitada"
                self.ui_logger.append(t("skill_status_updated").format(skill_id=skill_id, status=status))
                return True

            return False

        except Exception as e:
            self.ui_logger.append(t("error_updating_skill").format(skill_id=skill_id, error=e), LOGS.error)
            return False

    def get_available_skills(self) -> List[str]:
        if not self.enabled:
            return []

        try:
            res, _ = self.q_client.scroll(
                collection_name=self.collection_name,
                limit=1000,
                with_payload=True
            )
            return sorted(list(set(p.payload["skill_id"] for p in res if p.payload)))
        except Exception as e:
            self.ui_logger.append(t("error_get_available").format(error=e), LOGS.error)
            return []

    def get_enabled_skills(self) -> List[str]:
        if not self.enabled:
            return []

        try:
            res, _ = self.q_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=[FieldCondition(key="enabled", match=MatchValue(value=True))]),
                limit=1000,
                with_payload=True
            )
            return sorted(list(set(p.payload["skill_id"] for p in res if p.payload)))
        except Exception as e:
            self.ui_logger.append(t("error_get_enabled").format(error=e), LOGS.error)
            return []

    def cleanup(self):
        """Libera recursos de los modelos de ML para evitar leaks de procesos."""
        try:
            if hasattr(self, 'embedding_model') and self.embedding_model:
                del self.embedding_model
                self.embedding_model = None
                self.ui_logger.append(t("cleanup_embedding_completed"), LOGS.info)

            if hasattr(self, 'ranker') and self.ranker:
                del self.ranker
                self.ranker = None
                self.ui_logger.append(t("cleanup_ranker_completed"), LOGS.info)

            if hasattr(self, 'q_client') and self.q_client:
                try:
                    self.q_client.close()
                except Exception:
                    pass
                self.q_client = None
                self.ui_logger.append(t("cleanup_qdrant_completed"), LOGS.info)

            import gc
            gc.collect()
            self.ui_logger.append(t("cleanup_gc_completed"), LOGS.info)

        except Exception as e:
            self.ui_logger.append(t("cleanup_error").format(error=e), LOGS.error)

    def reset_db(self):
        if not self.enabled:
            return
        self.q_client.delete_collection(self.collection_name)
        self._init_collection()

    def get_skills_full(self, active_skills_ids: List[str]) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []

        try:
            res, _ = self.q_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=[
                    FieldCondition(key="enabled", match=MatchValue(value=True)),
                    FieldCondition(key="skill_id", match=MatchAny(any=active_skills_ids))
                ]),
                limit=1000,
                with_payload=True
            )
            return [{"text": p.payload["text"], "skill": p.payload["skill_id"]} for p in res]
        except Exception as e:
            self.ui_logger.append(t("error_get_skills_full").format(error=e), LOGS.error)
            return []

    def delete_skill(self, skill_id: str) -> bool:
        if not self.enabled:
            return False

        try:
            self.q_client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(must=[
                    FieldCondition(key="skill_id", match=MatchValue(value=skill_id))
                ])
            )
            self.ui_logger.append(t("skill_deleted_qdrant").format(skill_id=skill_id), LOGS.info)
            return True
        except Exception as e:
            self.ui_logger.append(t("error_deleting_skill").format(error=e), LOGS.error)
            return False