# PBT System API Reference

## Overview
The Population-Based Training (PBT) system provides a comprehensive framework for optimizing multi-agent reinforcement learning with correlation-driven insights and automated performance tracking.

## Core Components

### 1. Agent Configuration (`pbt/agent.py`)

#### `Agent` Class
```python
class Agent:
    def __init__(self, agent_id: int, config: Dict[str, Any])
```

**Parameters:**
- `agent_id`: Unique identifier for the agent
- `config`: Configuration dictionary with hyperparameters

**Key Methods:**
- `get_hyperparameters()`: Returns current hyperparameters
- `set_hyperparameters(params)`: Updates hyperparameters
- `calculate_performance()`: Computes performance metrics
- `meets_targets(targets)`: Checks target achievement

**Configuration Keys:**
```python
{
    'learning_rate': float,      # 0.0001 - 0.01
    'epsilon': float,            # 0.05 - 0.35
    'batch_size': int,           # 32 - 512
    'reward_shaping': bool,      # True/False
    'exploration_bonus': float,  # 0.0 - 0.1
    'archetype': str            # 'conservative', 'aggressive', 'balanced', 'explorer'
}
```

### 2. Training Management (`pbt/trainer.py`)

#### `PBTTrainer` Class
```python
class PBTTrainer:
    def __init__(self, population_size: int = 8, environment_type: str = "generic")
```

**Parameters:**
- `population_size`: Number of agents in population (4-16 recommended)
- `environment_type`: Type of RL environment ("navigation", "game", "control", "generic")

**Key Methods:**
- `train_generation(generation: int)`: Trains one generation
- `evaluate_agents()`: Evaluates all agents in population
- `get_population_metrics()`: Returns population-level statistics

**Usage Example:**
```python
trainer = PBTTrainer(population_size=8, environment_type="navigation")
for gen in range(20):
    trainer.train_generation(gen)
    metrics = trainer.evaluate_agents()
    print(f"Generation {gen}: {metrics}")
```

### 3. Population Scheduling (`pbt/scheduler.py`)

#### `PBTScheduler` Class
```python
class PBTScheduler:
    def __init__(self, population_size: int, targets: Dict[str, float])
```

**Key Methods:**
- `schedule_generation(agents, metrics)`: Determines exploit/explore decisions
- `mutate_hyperparameters(agent)`: Applies adaptive mutations
- `select_parents(agents, scores)`: Selects high-performing agents for reproduction

**Target Configuration:**
```python
targets = {
    'zero_rate': 0.08,          # <8% failure rate
    'success_rate': 0.15,       # >15% success rate
    'excellence_rate': 0.10,    # >10% excellence rate
    'mean_value': 0.35          # >0.35 mean performance
}
```

### 4. PBT Execution (`pbt/pbt_runner.py`)

#### `PBTRunner` Class
```python
class PBTRunner:
    def __init__(self, config_path: str = "pbt/configs/base.yaml")
```

**Command Line Interface:**
```bash
python pbt/pbt_runner.py --generations 20 --population 8 --mock
python pbt/pbt_runner.py --config custom_config.yaml --output-dir results
```

**Arguments:**
- `--generations`: Number of generations to run (default: 10)
- `--population`: Population size (default: 8)
- `--mock`: Use mock environment for testing
- `--config`: Path to configuration file
- `--output-dir`: Directory for results

### 5. Integration Hook (`pbt/integration_hook.py`)

#### `PBTIntegrationHook` Class
```python
class PBTIntegrationHook:
    def __init__(self, output_dir: str = "pbt/analysis")
```

**Key Methods:**
- `convert_pbt_logs(log_dir)`: Converts PBT logs to analysis format
- `generate_agent_dumps(agents)`: Creates agent dump files
- `run_consistency_analysis()`: Executes consistency analysis

**Integration with Existing Pipeline:**
```python
hook = PBTIntegrationHook("pbt/analysis")
hook.convert_pbt_logs("pbt/logs")
hook.run_consistency_analysis()

# Now use existing analysis tools
os.system("python scripts/analyze_agent_dump.py --consistency --dir pbt/analysis")
```

## Visualization Tools

### 1. PBT Results Visualization (`pbt/visualize_pbt_results.py`)

#### `PBTResultsVisualizer` Class
```python
class PBTResultsVisualizer:
    def __init__(self, output_dir: str = "pbt/visualizations")
```

**Usage:**
```bash
python pbt/visualize_pbt_results.py --pbt-dir pbt/analysis --output-dir visualizations
```

**Generated Plots:**
- `pbt_strategy_space.png`: Strategy space analysis
- Shows agent diversity and target achievement

### 2. Enhanced Performance Comparison (`pbt/enhanced_performance_comparison.py`)

#### `EnhancedPerformanceComparator` Class
```python
class EnhancedPerformanceComparator:
    def __init__(self, output_dir: str = "pbt/analysis_output")
```

**Usage:**
```bash
python pbt/enhanced_performance_comparison.py --baseline-dir data --pbt-dir pbt/analysis
```

**Generated Outputs:**
- `performance_comparison.png`: Baseline vs PBT comparison
- Performance summary with target achievement status

## Configuration System

### Base Configuration (`pbt/configs/base.yaml`)

```yaml
population:
  size: 8
  generations: 20

environment:
  type: "generic"
  mock: true

targets:
  zero_rate: 0.08
  success_rate: 0.15
  excellence_rate: 0.10
  mean_value: 0.35

hyperparameters:
  learning_rate:
    min: 0.0001
    max: 0.01
    mutation_std: 0.0005
  
  epsilon:
    min: 0.05
    max: 0.35
    mutation_std: 0.02
  
  batch_size:
    values: [32, 64, 128, 256, 512]
  
  reward_shaping:
    probability: 0.7
  
  exploration_bonus:
    min: 0.0
    max: 0.1
    mutation_std: 0.005

archetypes:
  conservative:
    learning_rate: 0.0005
    epsilon: 0.1
    reward_shaping: true
  
  aggressive:
    learning_rate: 0.005
    epsilon: 0.25
    exploration_bonus: 0.05
  
  balanced:
    learning_rate: 0.002
    epsilon: 0.15
    reward_shaping: true
  
  explorer:
    learning_rate: 0.001
    epsilon: 0.35
    exploration_bonus: 0.1

correlation_insights:
  zero_vs_excellence: -0.334585
  excellence_vs_mean: 0.617964
  zero_vs_success: 0.954509
```

## Error Handling

### Common Exceptions

#### `PBTConfigurationError`
```python
class PBTConfigurationError(Exception):
    """Raised when PBT configuration is invalid"""
```

#### `EnvironmentError`
```python
class EnvironmentError(Exception):
    """Raised when environment setup fails"""
```

#### `PopulationError`
```python
class PopulationError(Exception):
    """Raised when population management fails"""
```

### Error Handling Example:
```python
try:
    runner = PBTRunner("invalid_config.yaml")
    runner.run()
except PBTConfigurationError as e:
    print(f"Configuration error: {e}")
except EnvironmentError as e:
    print(f"Environment error: {e}")
```

## Integration Examples

### 1. Basic PBT Run
```python
# Run PBT with default settings
runner = PBTRunner()
results = runner.run(generations=10, population_size=8)

# Analyze results
visualizer = PBTResultsVisualizer()
visualizer.plot_basic_comparison(results)
```

### 2. Custom Environment Integration
```python
# Custom environment setup
config = {
    'environment_type': 'navigation',
    'reward_shaping_config': {
        'partial_progress_reward': 0.1,
        'near_success_reward': 0.2
    }
}

trainer = PBTTrainer(environment_type="navigation")
# ... training loop
```

### 3. Analysis Pipeline Integration
```python
# Run PBT
runner = PBTRunner()
runner.run(generations=20)

# Convert to analysis format
hook = PBTIntegrationHook()
hook.convert_pbt_logs("pbt/logs")

# Run existing analysis
os.system("python scripts/analyze_agent_dump.py --consistency --dir pbt/analysis")

# Compare with baseline
comparator = EnhancedPerformanceComparator()
comparator.compare_performance(baseline_data, pbt_data)
```

## Performance Metrics

### Core Metrics
- **Zero Rate**: Percentage of episodes with zero reward (target: <8%)
- **Success Rate**: Percentage of episodes with reward >0.75 (target: >15%)
- **Excellence Rate**: Percentage of episodes with reward >0.9 (target: >10%)
- **Mean Value**: Average reward across all episodes (target: >0.35)

### Population Metrics
- **Diversity**: Standard deviation across agents
- **Consistency**: Measure of agent similarity
- **Target Achievement**: Percentage of agents meeting targets

### Correlation Insights
- **Zero vs Excellence**: -0.334585 (reducing failures boosts excellence)
- **Excellence vs Mean**: 0.617964 (excellence strongly correlates with mean performance)
- **Zero vs Success**: 0.954509 (failure and success rates are highly correlated)

## Troubleshooting

### Common Issues

1. **PyTorch Not Installed**
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r pbt/requirements.txt
   ```

3. **Configuration Errors**
   - Check YAML syntax
   - Verify hyperparameter ranges
   - Ensure target values are realistic

4. **Memory Issues**
   - Reduce population size
   - Decrease episode length
   - Use CPU-only PyTorch

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

runner = PBTRunner()
runner.run(debug=True)
```

## Best Practices

### 1. Population Size
- Start with 8 agents for testing
- Scale to 16-32 for production
- Ensure computational resources can handle the load

### 2. Target Setting
- Use baseline analysis to set realistic targets
- Phase 1: 33% improvement in key metrics
- Long-term: 50%+ improvement

### 3. Hyperparameter Ranges
- Learning rate: 0.0001 - 0.01 (log scale)
- Epsilon: 0.05 - 0.35 (linear scale)
- Batch size: Powers of 2 (32, 64, 128, 256, 512)

### 4. Monitoring
- Run consistency analysis every 5 generations
- Monitor target achievement rates
- Track population diversity metrics

### 5. Environment Customization
- Implement proper reward shaping for your domain
- Define clear success/failure criteria
- Ensure environment is deterministic for reproducibility

## Version History

- **v1.0**: Initial PBT system with correlation insights
- **v1.1**: Added visualization tools and enhanced reporting
- **v1.2**: Integrated with existing analysis pipeline
- **v1.3**: Added comprehensive API documentation and troubleshooting

## Support

For issues and questions:
1. Check troubleshooting section
2. Review configuration examples
3. Run debug mode for detailed logging
4. Ensure all dependencies are installed

## License

This PBT system is part of the multi-agent reinforcement learning analysis pipeline and follows the same licensing terms as the parent project. 