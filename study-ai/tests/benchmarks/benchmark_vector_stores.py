"""Performance Benchmarks: Vector Stores

Compares FAISS vs alternatives for vector search.
"""

import pytest
import numpy as np
import time
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.mark.benchmark
class TestFAISSPerformance:
    """Benchmark FAISS vector operations."""
    
    def test_faiss_indexing_speed(self, benchmark):
        """Benchmark: Time to index 10k vectors."""
        import faiss
        
        dimension = 384
        num_vectors = 10000
        vectors = np.random.rand(num_vectors, dimension).astype('float32')
        
        def create_and_add():
            index = faiss.IndexFlatL2(dimension)
            index.add(vectors)  # type: ignore
            return index
        
        index = benchmark(create_and_add)
        
        assert index.ntotal == num_vectors
        print(f"\nIndexed {num_vectors:,} vectors in {benchmark.stats.stats.mean:.3f}s")
        print(f"Throughput: {num_vectors / benchmark.stats.stats.mean:,.0f} vectors/sec")
    
    def test_faiss_search_speed(self, benchmark):
        """Benchmark: Search time for single query."""
        import faiss
        
        dimension = 384
        num_vectors = 100000
        vectors = np.random.rand(num_vectors, dimension).astype('float32')
        
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)  # type: ignore
        
        query = np.random.rand(1, dimension).astype('float32')
        
        def search():
            D, I = index.search(query, k=5)  # type: ignore
            return I
        
        result = benchmark(search)
        
        assert len(result[0]) == 5
        print(f"\nSearch {num_vectors:,} vectors in {benchmark.stats.stats.mean * 1000:.2f}ms")
    
    def test_faiss_batch_search_speed(self):
        """Benchmark: Batch search performance."""
        import faiss
        
        dimension = 384
        num_index_vectors = 50000
        num_queries = 100
        
        index_vectors = np.random.rand(num_index_vectors, dimension).astype('float32')
        query_vectors = np.random.rand(num_queries, dimension).astype('float32')
        
        index = faiss.IndexFlatL2(dimension)
        index.add(index_vectors)  # type: ignore
        
        start = time.time()
        D, I = index.search(query_vectors, k=5)  # type: ignore
        elapsed = time.time() - start
        
        avg_per_query = (elapsed / num_queries) * 1000
        
        print(f"\nBatch Search Performance:")
        print(f"  Index size: {num_index_vectors:,} vectors")
        print(f"  Queries: {num_queries}")
        print(f"  Total time: {elapsed:.3f}s")
        print(f"  Avg per query: {avg_per_query:.2f}ms")
        
        assert avg_per_query < 50, "Average search should be < 50ms"


@pytest.mark.benchmark
class TestFAISSVsAlternatives:
    """Compare FAISS against alternative implementations."""
    
    def test_faiss_vs_numpy_linear_search(self):
        """Compare FAISS vs naive numpy implementation."""
        dimension = 384
        num_vectors = 10000
        
        vectors = np.random.rand(num_vectors, dimension).astype('float32')
        query = np.random.rand(dimension).astype('float32')
        
        # FAISS implementation
        import faiss
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)  # type: ignore
        
        start = time.time()
        for _ in range(100):
            D, I = index.search(query.reshape(1, -1), k=5)  # type: ignore
        faiss_time = (time.time() - start) / 100
        
        # Naive numpy implementation
        def numpy_search(query, vectors, k=5):
            distances = np.linalg.norm(vectors - query, axis=1)
            indices = np.argpartition(distances, k)[:k]
            return indices[np.argsort(distances[indices])]
        
        start = time.time()
        for _ in range(100):
            indices = numpy_search(query, vectors, k=5)
        numpy_time = (time.time() - start) / 100
        
        speedup = numpy_time / faiss_time
        
        print(f"\nFAISS vs NumPy ({num_vectors:,} vectors):")
        print(f"  FAISS: {faiss_time * 1000:.2f}ms")
        print(f"  NumPy: {numpy_time * 1000:.2f}ms")
        print(f"  Speedup: {speedup:.1f}x")
        
        assert speedup > 1.5, "FAISS should be significantly faster"
    
    def test_storage_efficiency(self):
        """Compare storage requirements."""
        dimension = 384
        num_vectors = 500000  # 500k vectors (100 students, 5k each)
        
        # Float32: 4 bytes per value
        bytes_per_vector = dimension * 4
        total_bytes = num_vectors * bytes_per_vector
        total_mb = total_bytes / (1024 * 1024)
        
        print(f"\nStorage Requirements ({num_vectors:,} vectors, {dimension}-dim):")
        print(f"  Raw vectors: {total_mb:.0f} MB")
        print(f"  With metadata (~100 bytes/vector): {(total_mb + (num_vectors * 100 / 1024 / 1024)):.0f} MB")
        print(f"  Per student (5k vectors): {(total_mb / 100):.1f} MB")
        
        # Conclusion: ~5MB per student with FAISS
        # Pinecone charges per vector count, not storage
        assert total_mb < 1000, "Should fit in < 1GB for 500k vectors"


@pytest.mark.benchmark
class TestVectorDBCostComparison:
    """Cost analysis: FAISS vs cloud vector DBs."""
    
    def test_pinecone_cost_calculator(self):
        """Calculate equivalent Pinecone cost."""
        
        # StudyAI scale
        students = 100
        vectors_per_student = 5000
        total_vectors = students * vectors_per_student
        
        # Pinecone pricing (2026)
        # Starter: $70/month for 100k vectors
        # Standard: $140/pod/month (1M vectors)
        
        pods_needed = (total_vectors // 100000) + 1
        pinecone_monthly = pods_needed * 70
        pinecone_annual = pinecone_monthly * 12
        
        # FAISS cost
        faiss_cost = 0  # Free, local storage
        
        # Storage cost if using S3 (optional backup)
        storage_gb = (total_vectors * 384 * 4) / (1024**3)
        s3_monthly = storage_gb * 0.023  # $0.023/GB/month
        
        print(f"\nVector DB Cost Comparison ({total_vectors:,} vectors):")
        print(f"\nPinecone:")
        print(f"  Pods needed: {pods_needed}")
        print(f"  Monthly: ${pinecone_monthly}")
        print(f"  Annual: ${pinecone_annual:,}")
        
        print(f"\nFAISS (local):")
        print(f"  Cost: $0")
        print(f"  Optional S3 backup: ${s3_monthly:.2f}/month")
        
        print(f"\nSavings: ${pinecone_annual:,}/year")
        
        assert faiss_cost == 0
        assert pinecone_annual > 4000, "Pinecone should cost > $4k/year at scale"
    
    def test_weaviate_cost_calculator(self):
        """Calculate Weaviate cloud cost."""
        
        students = 100
        total_vectors = students * 5000
        
        # Weaviate Cloud pricing
        # Standard: $25/month/million vectors
        weaviate_monthly = (total_vectors / 1_000_000) * 25
        weaviate_annual = weaviate_monthly * 12
        
        # Or self-host (Docker) = $0 but operational complexity
        
        print(f"\nWeaviate Cost ({total_vectors:,} vectors):")
        print(f"  Cloud: ${weaviate_monthly:.2f}/month (${weaviate_annual:.2f}/year)")
        print(f"  Self-host: $0 (Docker complexity)")
        print(f"  FAISS: $0 (simplest)")
        
        # For educational use, FAISS wins on simplicity + cost
        assert weaviate_monthly < 20, "Should be relatively cheap for 500k vectors"
