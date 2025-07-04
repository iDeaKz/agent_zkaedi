"""
Enhanced Population-Based Training Scheduler.
Integrates with our correlation analysis insights and performance targets.

Key enhancements:
- Target-aware exploit/explore decisions
- Correlation-based performance scoring
- Integration with our analysis pipeline
- Adaptive mutation strategies
"""
import copy
import json
import statistics
from pathlib import Path
from typing import List, Tuple, Dict, Any, Callable
import numpy as np

from agent import AgentConfig
from trainer import EnhancedTrainer, Trainer


class EnhancedScheduler:
    """
    Enhanced PBT scheduler with correlation analysis integration.
    Optimizes for our specific targets: zero rate <8%, success rate >15%, etc.
    """
    
    def __init__(self, 
                 env_fn: Callable, 
                 pop_size: int = 8,
                 eval_steps: int = 500, 
                 exploit_frac: float = 0.5,
                 target_aware: bool = True,
                 adaptive_mutation: bool = True) -> None:
        """
        Initialize enhanced PBT scheduler.
        
        Args:
            env_fn: Function that creates environment instances
            pop_size: Population size (default 8)
            eval_steps: Steps per evaluation period
            exploit_frac: Fraction of population to exploit from
            target_aware: Use target-aware scoring
            adaptive_mutation: Adapt mutation based on performance
        """
        self.env_fn = env_fn
        self.pop_size = pop_size
        self.eval_steps = eval_steps
        self.exploit_frac = exploit_frac
        self.target_aware = target_aware
        self.adaptive_mutation = adaptive_mutation
        
        # Initialize population with diverse configurations
        self.trainers: List[Tuple[EnhancedTrainer, AgentConfig]] = []
        self._initialize_population()
        
        # Tracking
        self.generation = 0
        self.best_scores = []
        self.target_achievements = []
        
        # Ensure directories exist
        Path("pbt/logs").mkdir(parents=True, exist_ok=True)
        Path("pbt/output").mkdir(parents=True, exist_ok=True)
        
    def _initialize_population(self) -> None:
        """Initialize population with diverse configurations."""
        print(f"🧬 Initializing population of {self.pop_size} agents...")
        
        for i in range(self.pop_size):
            # Mix of baseline-informed and random configs for diversity
            if i < 4:
                config = AgentConfig.from_baseline_analysis(i)
            else:
                config = AgentConfig.random_init()
            
            trainer = EnhancedTrainer(self.env_fn(), config, agent_id=i)
            self.trainers.append((trainer, config))
            
            print(f"Agent {i}: {config}")
    
    def step_generation(self) -> Dict[str, Any]:
        """
        Execute one generation of PBT.
        Returns generation statistics.
        """
        print(f"\n🔄 Generation {self.generation}")
        print("=" * 50)
        
        # Evaluate all agents
        scores = []
        detailed_metrics = []
        
        for i, (trainer, config) in enumerate(self.trainers):
            # Reset metrics for clean evaluation
            trainer.reset_metrics()
            
            # Train and evaluate
            total_reward = trainer.train_steps(self.eval_steps)
            
            # Get comprehensive metrics
            metrics = trainer.get_metrics()
            performance_score = trainer.get_performance_score()
            
            scores.append(performance_score)
            detailed_metrics.append({
                'agent_id': i,
                'total_reward': total_reward,
                'performance_score': performance_score,
                'config': config.asdict(),
                'metrics': metrics,
                'targets_met': sum(config.meets_targets().values())
            })
            
            print(f"Agent {i}: score={performance_score:.3f}, "
                  f"zero_rate={metrics['zero_rate']:.3f}, "
                  f"success_rate={metrics['success_rate']:.3f}, "
                  f"targets_met={sum(config.meets_targets().values())}/4")
        
        # Rank agents by performance
        ranked = sorted(zip(scores, self.trainers, detailed_metrics), 
                       key=lambda x: -x[0])
        
        # Log generation results
        gen_stats = self._log_generation(ranked)
        
        # Exploit and explore
        self._exploit_and_explore(ranked)
        
        # Save best checkpoints
        self._save_checkpoints(ranked)
        
        self.generation += 1
        return gen_stats
    
    def _log_generation(self, ranked: List) -> Dict[str, Any]:
        """Log generation results with detailed metrics."""
        gen_data = {
            "generation": self.generation,
            "timestamp": str(Path().resolve()),
            "population_size": self.pop_size,
            "eval_steps": self.eval_steps,
            "agents": []
        }
        
        # Collect agent data
        best_score = ranked[0][0]
        worst_score = ranked[-1][0]
        mean_score = statistics.mean([score for score, _, _ in ranked])
        
        # Target achievement statistics
        target_achievements = []
        zero_rates = []
        success_rates = []
        excellence_rates = []
        
        for score, (trainer, config), metrics in ranked:
            agent_data = {
                "id": metrics['agent_id'],
                "score": score,
                "total_reward": metrics['total_reward'],
                "performance_score": metrics['performance_score'],
                "targets_met": metrics['targets_met'],
                **config.asdict(),
                **metrics['metrics']
            }
            gen_data["agents"].append(agent_data)
            
            # Collect statistics
            target_achievements.append(metrics['targets_met'])
            zero_rates.append(metrics['metrics']['zero_rate'])
            success_rates.append(metrics['metrics']['success_rate'])
            excellence_rates.append(metrics['metrics']['excellence_rate'])
        
        # Generation summary
        gen_data["summary"] = {
            "best_score": best_score,
            "worst_score": worst_score,
            "mean_score": mean_score,
            "std_score": statistics.stdev([score for score, _, _ in ranked]),
            "mean_targets_met": statistics.mean(target_achievements),
            "agents_meeting_all_targets": sum(1 for t in target_achievements if t == 4),
            "population_metrics": {
                "mean_zero_rate": statistics.mean(zero_rates),
                "mean_success_rate": statistics.mean(success_rates),
                "mean_excellence_rate": statistics.mean(excellence_rates),
                "std_zero_rate": statistics.stdev(zero_rates),
                "std_success_rate": statistics.stdev(success_rates),
                "std_excellence_rate": statistics.stdev(excellence_rates)
            }
        }
        
        # Save to file
        log_path = Path(f"pbt/logs/gen_{self.generation}.json")
        with open(log_path, "w") as f:
            json.dump(gen_data, f, indent=2, default=self._json_serializer)
        
        # Console output
        print(f"\n📊 Generation {self.generation} Summary:")
        print(f"Best score: {best_score:.3f}")
        print(f"Mean score: {mean_score:.3f} ± {gen_data['summary']['std_score']:.3f}")
        print(f"Agents meeting all targets: {gen_data['summary']['agents_meeting_all_targets']}/{self.pop_size}")
        print(f"Population zero rate: {gen_data['summary']['population_metrics']['mean_zero_rate']:.3f}")
        print(f"Population success rate: {gen_data['summary']['population_metrics']['mean_success_rate']:.3f}")
        
        # Track progress
        self.best_scores.append(best_score)
        self.target_achievements.append(gen_data['summary']['agents_meeting_all_targets'])
        
        return gen_data
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for numpy types and other non-serializable objects."""
        import numpy as np
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def _exploit_and_explore(self, ranked: List) -> None:
        """Enhanced exploit/explore with adaptive mutation."""
        n_exploit = int(self.pop_size * self.exploit_frac)
        best_segment = ranked[:n_exploit]
        
        print(f"\n🔬 Exploit/Explore: top {n_exploit} agents")
        
        # Exploit: replace worst performers with mutated versions of best
        for idx in range(n_exploit, self.pop_size):
            # Select parent from best segment
            parent_idx = idx % n_exploit
            parent_score, (parent_trainer, parent_config), parent_metrics = best_segment[parent_idx]
            
            # Create mutated child config
            child_config = copy.deepcopy(parent_config)
            
            # Adaptive mutation based on performance
            if self.adaptive_mutation:
                # More aggressive mutation if targets not met
                targets_met = parent_metrics['targets_met']
                if targets_met < 2:
                    mutation_strength = 0.3  # Aggressive
                elif targets_met < 3:
                    mutation_strength = 0.2  # Moderate
                else:
                    mutation_strength = 0.1  # Conservative
            else:
                mutation_strength = 0.2
            
            child_config.mutate(sigma=mutation_strength)
            
            # Create new trainer with mutated config
            child_trainer = EnhancedTrainer(self.env_fn(), child_config, agent_id=idx)
            
            # Replace in population
            self.trainers[idx] = (child_trainer, child_config)
            
            print(f"Agent {idx}: mutated from agent {parent_idx} "
                  f"(targets: {parent_metrics['targets_met']}/4, "
                  f"mutation: {mutation_strength:.1f})")
    
    def _save_checkpoints(self, ranked: List) -> None:
        """Save checkpoints of best performers."""
        # Save top 3 agents
        for i, (score, (trainer, config), metrics) in enumerate(ranked[:3]):
            agent_id = metrics['agent_id']
            checkpoint_path = Path(f"pbt/output/gen_{self.generation}_agent_{agent_id}.pt")
            trainer.save_checkpoint(checkpoint_path)
            
            # Also save config
            config_path = Path(f"pbt/output/gen_{self.generation}_agent_{agent_id}_config.json")
            config.to_json(config_path)
    
    def get_best_agent(self) -> Tuple[EnhancedTrainer, AgentConfig, Dict[str, Any]]:
        """Get the current best performing agent."""
        # Evaluate current population
        best_score = -float('inf')
        best_trainer = None
        best_config = None
        best_metrics = None
        
        for trainer, config in self.trainers:
            trainer.reset_metrics()
            trainer.train_steps(self.eval_steps // 2)  # Quick evaluation
            score = trainer.get_performance_score()
            
            if score > best_score:
                best_score = score
                best_trainer = trainer
                best_config = config
                best_metrics = trainer.get_metrics()
        
        return best_trainer, best_config, best_metrics
    
    def run_training(self, n_generations: int) -> Dict[str, Any]:
        """
        Run full PBT training for n generations.
        Returns training summary.
        """
        print(f"🚀 Starting PBT training for {n_generations} generations")
        print(f"Population size: {self.pop_size}")
        print(f"Evaluation steps: {self.eval_steps}")
        print(f"Target-aware scoring: {self.target_aware}")
        print(f"Adaptive mutation: {self.adaptive_mutation}")
        print("=" * 60)
        
        generation_stats = []
        
        for gen in range(n_generations):
            gen_stats = self.step_generation()
            generation_stats.append(gen_stats)
            
            # Early stopping if all agents meet targets
            if gen_stats['summary']['agents_meeting_all_targets'] == self.pop_size:
                print(f"\n🎉 All agents meet targets! Stopping at generation {gen}")
                break
        
        # Final summary
        final_summary = {
            "total_generations": len(generation_stats),
            "final_best_score": self.best_scores[-1] if self.best_scores else 0,
            "best_score_achieved": max(self.best_scores) if self.best_scores else 0,
            "final_targets_met": self.target_achievements[-1] if self.target_achievements else 0,
            "max_targets_met": max(self.target_achievements) if self.target_achievements else 0,
            "generation_stats": generation_stats
        }
        
        # Save final summary
        with open("pbt/logs/training_summary.json", "w") as f:
            json.dump(final_summary, f, indent=2, default=self._json_serializer)
        
        print(f"\n🏁 Training complete!")
        print(f"Best score achieved: {final_summary['best_score_achieved']:.3f}")
        print(f"Max agents meeting targets: {final_summary['max_targets_met']}/{self.pop_size}")
        
        return final_summary


# Backward compatibility with original scaffold
class Scheduler(EnhancedScheduler):
    """Backward compatibility wrapper."""
    
    def __init__(self, env_fn, pop_size: int = 8, eval_steps: int = 500, 
                 exploit_frac: float = 0.5) -> None:
        super().__init__(env_fn, pop_size, eval_steps, exploit_frac, 
                        target_aware=True, adaptive_mutation=True)
        
        # Convert to original trainer format for compatibility
        self.trainers = [(Trainer(self.env_fn(), config), config) 
                        for _, config in self.trainers]
    
    def step_generation(self) -> None:
        """Original interface."""
        super().step_generation()


if __name__ == "__main__":
    # Test the enhanced scheduler
    print("🧪 Testing Enhanced PBT Scheduler")
    print("=" * 50)
    
    # Mock environment
    class MockEnv:
        def __init__(self):
            self.observation_space = type('', (), {'shape': (4,)})()
            self.action_space = type('', (), {'n': 2})()
            
        def reset(self):
            return np.random.randn(4)
            
        def step(self, action):
            return np.random.randn(4), np.random.random(), False, {}
    
    # Test scheduler
    def make_env():
        return MockEnv()
    
    scheduler = EnhancedScheduler(make_env, pop_size=4, eval_steps=100)
    
    # Run a few generations
    print("\n🔄 Running test generations...")
    for i in range(3):
        stats = scheduler.step_generation()
        print(f"Generation {i}: {stats['summary']['agents_meeting_all_targets']}/4 agents meeting targets")
    
    # Test best agent retrieval
    best_trainer, best_config, best_metrics = scheduler.get_best_agent()
    print(f"\nBest agent: {best_config}")
    print(f"Best metrics: {best_metrics}")
    
    print("\n✅ Enhanced PBT Scheduler Ready!") 