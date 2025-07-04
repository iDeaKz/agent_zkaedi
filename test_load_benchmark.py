# benchmarks/test_load_benchmark.py
import pytest
import asyncio
from project_module.core import (
    compute_heavy, 
    BlockchainAPI, 
    VectorEmbeddingOptimizer,
    ERCStandard
)
from project_module.utils import vector_embedding_optimizer

@pytest.mark.benchmark(group="compute")
def test_compute_heavy_benchmark(benchmark):
    """Benchmark compute_heavy function"""
    result = benchmark(lambda: compute_heavy(10, 20))
    assert result == 30

@pytest.mark.benchmark(group="compute")
def test_compute_heavy_large_numbers_benchmark(benchmark):
    """Benchmark compute_heavy with large numbers"""
    result = benchmark(lambda: compute_heavy(1000000, 2000000))
    assert result == 3000000

@pytest.mark.benchmark(group="optimization")
def test_vector_embedding_small_data_benchmark(benchmark):
    """Benchmark vector embedding optimization with small data"""
    small_data = {"key": "value", "number": 42}
    
    result = benchmark(
        lambda: vector_embedding_optimizer(small_data, strategy="performance")
    )
    
    assert result["_optimization"] == "performance"

@pytest.mark.benchmark(group="optimization")
def test_vector_embedding_large_data_benchmark(benchmark):
    """Benchmark vector embedding optimization with large data"""
    large_data = {f"key_{i}": f"value_{i}" * 10 for i in range(1000)}
    
    result = benchmark(
        lambda: vector_embedding_optimizer(large_data, strategy="memory")
    )
    
    assert result["_optimization"] == "memory"

@pytest.mark.benchmark(group="optimization")
def test_vector_optimizer_class_benchmark(benchmark):
    """Benchmark VectorEmbeddingOptimizer class"""
    optimizer = VectorEmbeddingOptimizer()
    test_data = {"transaction": "0x123", "amount": 1000, "gas": 21000}
    
    result = benchmark(lambda: optimizer.optimize_response(test_data))
    
    assert result["_embedding_optimized"] is True

@pytest.mark.benchmark(group="blockchain")
def test_blockchain_api_call_benchmark(benchmark):
    """Benchmark blockchain API contract call"""
    api = BlockchainAPI("testnet")
    
    async def make_call():
        return await api.call_contract(
            "0x1234567890123456789012345678901234567890",
            "balanceOf",
            ["0xabcdef1234567890123456789012345678901234"],
            ERCStandard.ERC20
        )
    
    # Create a new event loop for benchmarking
    loop = asyncio.new_event_loop()
    result = benchmark(lambda: loop.run_until_complete(make_call()))
    loop.close()
    
    assert result["success"] is True

@pytest.mark.benchmark(group="blockchain")
def test_multiple_blockchain_calls_benchmark(benchmark):
    """Benchmark multiple blockchain API calls"""
    api = BlockchainAPI("testnet")
    
    async def make_multiple_calls():
        results = []
        for i in range(10):
            result = await api.call_contract(
                f"0x{i:040x}",
                "transfer",
                ["0xrecipient", 100 * i],
                ERCStandard.ERC20
            )
            results.append(result)
        return results
    
    loop = asyncio.new_event_loop()
    results = benchmark(lambda: loop.run_until_complete(make_multiple_calls()))
    loop.close()
    
    assert len(results) == 10
    assert all(r["success"] for r in results)

@pytest.mark.benchmark(group="optimization")
def test_optimization_strategy_comparison(benchmark):
    """Compare different optimization strategies"""
    test_data = {f"key_{i}": f"value_{i}" for i in range(100)}
    
    @benchmark
    def run_all_strategies():
        results = {}
        for strategy in ["auto", "performance", "accuracy", "memory"]:
            results[strategy] = vector_embedding_optimizer(test_data, strategy=strategy)
        return results
    
    assert len(run_all_strategies) == 4

# Parametrized benchmarks for different data sizes
@pytest.mark.parametrize("data_size", [10, 100, 1000, 10000])
@pytest.mark.benchmark(group="scaling")
def test_vector_optimization_scaling(benchmark, data_size):
    """Test how vector optimization scales with data size"""
    data = {f"key_{i}": f"value_{i}" for i in range(data_size)}
    
    result = benchmark(
        lambda: vector_embedding_optimizer(data, strategy="auto")
    )
    
    assert "_optimization" in result

# Memory-intensive benchmark
@pytest.mark.benchmark(group="memory")
def test_memory_optimization_benchmark(benchmark):
    """Benchmark memory optimization with data containing many None values"""
    data_with_nones = {}
    for i in range(1000):
        if i % 3 == 0:
            data_with_nones[f"key_{i}"] = None
        else:
            data_with_nones[f"key_{i}"] = f"value_{i}"
    
    result = benchmark(
        lambda: vector_embedding_optimizer(data_with_nones, strategy="memory")
    )
    
    # Check that None values were removed
    non_meta_keys = [k for k in result.keys() if not k.startswith("_")]
    assert all(result[k] is not None for k in non_meta_keys) 