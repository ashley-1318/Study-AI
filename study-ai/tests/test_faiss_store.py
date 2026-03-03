"""Component Tests: FAISS Vector Store

Tests for FAISS index operations, concurrent access, and metadata consistency.
"""

import pytest
import numpy as np
import tempfile
import json
from pathlib import Path
import sys
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from tools.faiss_store import FAISSStore  # type: ignore


class TestFAISSStore:
    """Test suite for FAISS vector store operations."""
    
    @pytest.fixture
    def faiss_store(self):
        """Create a FAISS store instance."""
        user_id = f"test_user_{random.randint(1000, 9999)}"
        store = FAISSStore(user_id=user_id)
        store.load()
        return store
    
    def test_create_index(self, faiss_store, temp_faiss_dir):
        """Test creating a new FAISS index."""
        embeddings = np.random.rand(10, 384).astype('float32')
        metadata = [{"text": f"Chunk {i}", "material_id": "mat_1"} for i in range(10)]
        
        # Add embeddings and verify IDs returned
        ids = faiss_store.add(embeddings, metadata)
        
        assert len(ids) == 10, "Should return 10 IDs for 10 embeddings"
        assert all(isinstance(id, str) for id in ids), "IDs should be strings"
    
    def test_add_and_search(self, faiss_store):
        """Test adding vectors and searching."""
        # Add vectors
        embeddings = np.random.rand(100, 384).astype('float32')
        metadata = [{"text": f"Document {i}", "material_id": "mat_1", "chunk_idx": i} for i in range(100)]
        
        vector_ids = faiss_store.add(embeddings, metadata)
        assert len(vector_ids) == 100, "Should return 100 IDs"
        
        # Search with a query vector
        query = embeddings[0]  # Should return itself as top result
        results = faiss_store.search(query, top_k=5)
        
        assert len(results) <= 5, "Should return at most 5 results"
        assert len(results) > 0, "Should return at least 1 result"
        # First result should be the closest match
        assert results[0]["text"] == "Document 0", "First result should be the query itself"
    
    def test_metadata_consistency(self, faiss_store):
        """Test that metadata stays synchronized with vectors."""
        embeddings = np.random.rand(50, 384).astype('float32')
        metadata = [
            {"text": f"Chunk {i}", "material_id": f"mat_{i % 5}", "page": i // 10}
            for i in range(50)
        ]
        
        vector_ids = faiss_store.add(embeddings, metadata)
        assert len(vector_ids) == 50
        
        # Search and verify metadata
        query = embeddings[25]
        results = faiss_store.search(query, top_k=1)
        
        assert len(results) > 0, "Should find at least one result"
        assert results[0]["text"] == "Chunk 25"
        assert results[0]["material_id"] == "mat_0"
        assert results[0]["page"] == 2
    
    def test_incremental_additions(self, faiss_store):
        """Test adding vectors in multiple batches."""
        # First batch
        emb1 = np.random.rand(20, 384).astype('float32')
        meta1 = [{"text": f"Batch1-{i}", "batch": 1} for i in range(20)]
        faiss_store.add(emb1, meta1)
        
        # Second batch
        emb2 = np.random.rand(30, 384).astype('float32')
        meta2 = [{"text": f"Batch2-{i}", "batch": 2} for i in range(30)]
        faiss_store.add(emb2, meta2)
        
        # Verify both batches are present
        query = emb1[0]
        results = faiss_store.search(query, top_k=10)
        
        batch1_count = sum(1 for r in results if r.get("batch") == 1)
        assert batch1_count > 0, "Should find results from first batch"
        
        # Total should be 50
        assert faiss_store.index.ntotal == 50, "Index should contain 50 vectors"
    
    def test_search_filtering_by_material(self, faiss_store):
        """Test filtering search results by material_id."""
        embeddings = np.random.rand(60, 384).astype('float32')
        metadata = [
            {"text": f"Chunk {i}", "material_id": f"mat_{i % 3}"}
            for i in range(60)
        ]
        
        faiss_store.add(embeddings, metadata)
        
        # Search and filter results
        query = embeddings[0]
        all_results = faiss_store.search(query, top_k=20)
        
        # Filter for mat_0
        mat_0_results = [r for r in all_results if r["material_id"] == "mat_0"]
        
        assert len(mat_0_results) > 0, "Should find results from mat_0"
    
    def test_persistence(self):
        """Test that index persists across instances."""
        user_id = f"persist_test_{random.randint(1000, 9999)}"
        
        # Create and save
        store1 = FAISSStore(user_id=user_id)
        store1.load()  # Initialize
        embeddings = np.random.rand(30, 384).astype('float32')
        metadata = [{"text": f"Doc {i}", "id": i} for i in range(30)]
        store1.add(embeddings, metadata)
        store1.save()
        
        # Load in new instance
        store2 = FAISSStore(user_id=user_id)
        store2.load()
        
        assert store2.index is not None, "Should load index"
        assert store2.index.ntotal >= 30, "Should load at least 30 vectors"
        
        # Search should work
        results = store2.search(embeddings[10], top_k=1)
        assert len(results) > 0, "Should return search results"
    
    @pytest.mark.benchmark
    def test_search_performance(self, faiss_store, benchmark):
        """Benchmark: Search speed with 10k vectors."""
        # Add 10k vectors
        embeddings = np.random.rand(10000, 384).astype('float32')
        metadata = [{"text": f"Chunk {i}"} for i in range(10000)]
        faiss_store.add(embeddings, metadata)
        
        query = np.random.rand(384).astype('float32')
        
        # Benchmark search
        results = benchmark(lambda: faiss_store.search(query, top_k=5))
        
        assert benchmark.stats.stats.mean < 0.05, "Search should take < 50ms"
        assert len(results) == 5
    
    @pytest.mark.slow
    def test_concurrent_reads(self, faiss_store):
        """Test concurrent read operations."""
        # Setup: Add data
        embeddings = np.random.rand(1000, 384).astype('float32')
        metadata = [{"text": f"Chunk {i}"} for i in range(1000)]
        faiss_store.add(embeddings, metadata)
        faiss_store.save()
        
        def search_task(task_id):
            query = embeddings[task_id % 1000]
            results = faiss_store.search(query, top_k=5)
            return len(results)
        
        # Execute 50 concurrent searches
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(search_task, i) for i in range(50)]
            results = [f.result() for f in as_completed(futures)]
        
        assert all(r == 5 for r in results), "All concurrent searches should succeed"
    
    def test_empty_index_search(self, faiss_store):
        """Test searching an empty index."""
        query = np.random.rand(384).astype('float32')
        results = faiss_store.search(query, top_k=5)
        
        assert results == [], "Empty index should return empty results"
    
    def test_dimension_mismatch(self, faiss_store):
        """Test error handling for wrong dimensions."""
        # Add 384-dim vectors
        embeddings = np.random.rand(10, 384).astype('float32')
        metadata = [{"text": f"Chunk {i}"} for i in range(10)]
        faiss_store.add(embeddings, metadata)
        
        # Try to search with wrong dimension
        wrong_query = np.random.rand(128).astype('float32')
        
        with pytest.raises(Exception):
            # Should raise dimension mismatch error
            faiss_store.search(wrong_query, top_k=5)


class TestFAISSVsAlternatives:
    """Comparative tests: FAISS vs in-memory dict and cloud alternatives."""
    
    @pytest.mark.benchmark
    def test_faiss_vs_naive_search(self, benchmark):
        """Compare FAISS vs naive linear search."""
        # Create test data
        embeddings = np.random.rand(5000, 384).astype('float32')
        query = np.random.rand(384).astype('float32')
        
        # Naive implementation
        def naive_search(query, embeddings, top_k=5):
            distances = []
            for i, emb in enumerate(embeddings):
                dist = np.linalg.norm(query - emb)
                distances.append((dist, i))
            distances.sort()
            return distances[:top_k]
        
        # FAISS implementation
        import faiss
        index = faiss.IndexFlatL2(384)
        index.add(embeddings)  # type: ignore
        
        def faiss_search(query):
            D, I = index.search(query.reshape(1, -1), top_k=5)  # type: ignore
            return list(zip(D[0], I[0]))
        
        # Benchmark both
        naive_time = benchmark(naive_search, query, embeddings)
        
        start = time.time()
        for _ in range(100):
            faiss_search(query)
        faiss_time = (time.time() - start) / 100
        
        print(f"\nSearch Performance (5000 vectors):")
        print(f"  Naive linear: {benchmark.stats.stats.mean * 1000:.2f}ms")
        print(f"  FAISS: {faiss_time * 1000:.2f}ms")
        print(f"  Speedup: {benchmark.stats.stats.mean / faiss_time:.1f}x")
        
        assert faiss_time < benchmark.stats.stats.mean, "FAISS should be faster"
    
    def test_cost_comparison_reference(self):
        """
        Cost comparison: FAISS vs Pinecone (reference, no API calls).
        
        Scenario: 100 students, avg 5000 vectors/student
        Total: 500,000 vectors
        
        FAISS:
        - Storage: ~750MB for 500k vectors (384-dim)
        - Cost: $0 (local disk)
        
        Pinecone Starter ($70/month):
        - Includes 100,000 vectors
        - Need 5 pods = $350/month
        - Annual cost: $4,200
        
        Savings: $4,200/year
        
        Trade-off: FAISS requires local storage vs Pinecone's managed service.
        For educational use: Local is preferable (privacy + portability).
        """
        students = 100
        vectors_per_student = 5000
        total_vectors = students * vectors_per_student
        
        # Storage calc (float32 = 4 bytes, 384 dims = 1536 bytes/vector)
        storage_mb = (total_vectors * 384 * 4) / (1024 * 1024)
        
        faiss_cost_annual = 0
        pinecone_pods_needed = total_vectors // 100_000
        pinecone_cost_annual = pinecone_pods_needed * 70 * 12
        
        print(f"\nVector DB Cost Comparison ({total_vectors:,} vectors):")
        print(f"  FAISS: ${faiss_cost_annual}/year ({storage_mb:.0f}MB local storage)")
        print(f"  Pinecone: ${pinecone_cost_annual:,}/year ({pinecone_pods_needed} pods)")
        print(f"  Savings: ${pinecone_cost_annual - faiss_cost_annual:,}/year")
        
        assert faiss_cost_annual == 0
        assert pinecone_cost_annual > 4000
