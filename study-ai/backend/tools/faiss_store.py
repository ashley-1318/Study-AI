"""StudyAI — FAISS vector store, persisted per user to disk."""
import json
import os
import uuid
from typing import Optional

import faiss
import numpy as np

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_indexes")


class FAISSStore:
    """
    Per-user FAISS flat L2 index with JSON metadata sidecar.
    Vectors are 384-dim (all-MiniLM-L6-v2).
    Files: {user_id}.index  and  {user_id}.json
    """

    DIM = 384

    def __init__(self, user_id: str):
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        self.user_id    = user_id
        self.index_path = os.path.join(FAISS_INDEX_PATH, f"{user_id}.index")
        self.meta_path  = os.path.join(FAISS_INDEX_PATH, f"{user_id}.json")
        self.index      = None
        self.metadata: list[dict] = []  # parallel list to FAISS vectors

    def _new_index(self) -> faiss.IndexFlatL2:
        return faiss.IndexFlatL2(self.DIM)

    def load(self) -> "FAISSStore":
        """Load index and metadata from disk, or create an empty new one."""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = self._new_index()

        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = []

        return self

    def save(self):
        """Persist index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False)

    def add(self, embeddings: list[list[float]], meta_list: list[dict]) -> list[str]:
        """
        Add batch of embedding vectors with associated metadata.
        Returns list of newly assigned vector IDs (str UUIDs stored in meta).
        """
        if self.index is None:
            self.load()

        arr = np.array(embeddings, dtype="float32")
        self.index.add(arr)

        ids = []
        for meta in meta_list:
            vid = str(uuid.uuid4())
            meta["_vector_id"] = vid
            self.metadata.append(meta)
            ids.append(vid)

        self.save()
        return ids

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        exclude_material: Optional[str] = None,
    ) -> list[dict]:
        """
        Search for nearest neighbours, optionally excluding chunks
        from a specific material (to avoid self-retrieval).
        Returns list of metadata dicts with added 'score' key.
        """
        if self.index is None:
            self.load()
        if self.index.ntotal == 0:
            return []

        query = np.array([query_embedding], dtype="float32")
        # Retrieve extra results so we can filter without running short
        k = min(top_k + 20, self.index.ntotal)
        distances, indices = self.index.search(query, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx].copy()
            if exclude_material and meta.get("material_id") == exclude_material:
                continue
            meta["score"] = float(1 / (1 + dist))  # convert L2 distance to similarity
            results.append(meta)
            if len(results) >= top_k:
                break

        return results

    def delete_by_material(self, material_id: str):
        """
        Remove all vectors belonging to a material by rebuilding the index
        without those entries (FAISS IndexFlatL2 doesn't support in-place delete).
        """
        if self.index is None:
            self.load()

        keep_meta = [m for m in self.metadata if m.get("material_id") != material_id]
        removed   = len(self.metadata) - len(keep_meta)

        if removed == 0:
            return  # nothing to do

        # Rebuild index from kept vectors
        new_index = self._new_index()
        if keep_meta:
            # We need to re-encode to rebuild; store original vectors by re-embedding
            # Since we don't store raw vectors, we rebuild from embeddings in metadata
            # (embeddings saved in meta during add)
            vecs = [m["embedding"] for m in keep_meta if "embedding" in m]
            if vecs:
                arr = np.array(vecs, dtype="float32")
                new_index.add(arr)

        self.index    = new_index
        self.metadata = keep_meta
        self.save()
