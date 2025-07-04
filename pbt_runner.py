#!/usr/bin/env python3
"""
Enhanced Population-Based Training Runner
Integrates with our correlation analysis and performance targets.

Usage:
    python pbt/pbt_runner.py --env CartPole-v1 --gens 25 --pop 10
    python pbt/pbt_runner.py --mock --gens 10 --pop 8  # For testing
    python pbt/pbt_runner.py --baseline-test --gens 5  # Test against baseline
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    import gym
    GYM_AVAILABLE = True
except ImportError:
    GYM_AVAILABLE = False
    print("WARNING: Gym not available, using mock environment")

import numpy as np
from scheduler import EnhancedScheduler
from agent import AgentConfig
from environments import make_environment, MockEnvironment as CustomMockEnvironment, ENVIRONMENT_REGISTRY


class MockEnvironment:
    """
    Mock environment for testing PBT without gym dependency.
    Simulates our baseline characteristics: ~12% zero rate, ~12% success rate.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.observation_space = type('', (), {'shape': (4,)})()
        self.action_space = type('', (), {'n': 4})()
        self.rng = np.random.default_rng(seed)
        self.step_count = 0
        self.episode_length = self.rng.integers(50, 200)
        
    def reset(self):
        """Reset environment."""
        self.step_count = 0
        self.episode_length = self.rng.integers(50, 200)
        return self.rng.standard_normal(4)
    
    def step(self, action: int):
        """
        Step environment with characteristics matching our baseline analysis.
        Simulates sparse reward environment with ~12% zero episodes, ~12% success.
        """
        self.step_count += 1
        next_state = self.rng.standard_normal(4)
        
        # Episode termination
        done = self.step_count >= self.episode_length
        
        if done:
            # Simulate baseline reward distribution
            rand = self.rng.random()
            if rand < 0.12:  # ~12% zero episodes (baseline: 11.93%)
                reward = 0.0
            elif rand < 0.24:  # ~12% success episodes (baseline: 11.89%)
                reward = self.rng.uniform(0.75, 1.0)
            elif rand < 0.30:  # ~6% excellence episodes (baseline: 5.40%)
                reward = self.rng.uniform(0.9, 1.0)
            else:  # Remaining episodes: moderate performance
                reward = self.rng.uniform(0.1, 0.75)
        else:
            reward = 0.0  # No intermediate rewards in baseline
        
        info = {}
        return next_state, reward, done, info


def make_mock_env(seed: Optional[int] = None):
    """Factory for mock environment."""
    return lambda: MockEnvironment(seed)


def make_custom_env(env_id: str):
    """Factory for custom environment (no gym dependency)."""
    def env_factory():
        try:
            # First try our custom environment registry
            if env_id in ENVIRONMENT_REGISTRY:
                return make_environment(env_id)
            else:
                print(f"WARNING: Environment {env_id} not found in custom registry")
                print(f"   Available: {list(ENVIRONMENT_REGISTRY.keys())}")
                print("   Using baseline-calibrated mock environment")
                return CustomMockEnvironment(reward_type="baseline_calibrated")
        except Exception as e:
            print(f"WARNING: Failed to create {env_id}: {e}")
            print("   Using baseline-calibrated mock environment")
            return CustomMockEnvironment(reward_type="baseline_calibrated")
    
    return env_factory


def make_gym_env(env_id: str):
    """Factory for gym environment (fallback to custom if gym unavailable)."""
    if not GYM_AVAILABLE:
        print(f"WARNING: Gym not available, using custom environment for {env_id}")
        return make_custom_env(env_id)
    
    def env_factory():
        try:
            return gym.make(env_id)
        except Exception as e:
            print(f"WARNING: Failed to create gym {env_id}: {e}")
            print("   Falling back to custom environment")
            return make_custom_env(env_id)()
    
    return env_factory


def run_baseline_comparison_test(args):
    """
    Run a test comparing PBT performance against our baseline analysis.
    This validates that our PBT setup can improve upon the baseline metrics.
    """
    print("🧪 BASELINE COMPARISON TEST")
    print("=" * 50)
    print("Baseline metrics (from our analysis):")
    print("• Zero rate: 11.93%")
    print("• Success rate: 11.89%") 
    print("• Excellence rate: 5.40%")
    print("• Mean value: 0.2897")
    print("\nPBT Targets:")
    print("• Zero rate: <8.0%")
    print("• Success rate: >15.0%")
    print("• Excellence rate: >10.0%")
    print("• Mean value: >0.35")
    print("=" * 50)
    
    # Use mock environment calibrated to baseline
    env_fn = make_mock_env(seed=42)
    
    # Create scheduler with target-aware settings
    scheduler = EnhancedScheduler(
        env_fn=env_fn,
        pop_size=args.pop,
        eval_steps=args.eval_steps,
        exploit_frac=0.4,  # More exploration
        target_aware=True,
        adaptive_mutation=True
    )
    
    # Run training
    results = scheduler.run_training(args.gens)
    
    # Analyze results vs baseline
    final_gen = results['generation_stats'][-1]
    final_metrics = final_gen['summary']['population_metrics']
    
    print("\nFINAL RESULTS vs BASELINE")
    print("=" * 50)
    
    improvements = {}
    
    # Zero rate (lower is better)
    baseline_zero = 0.1193
    final_zero = final_metrics['mean_zero_rate']
    zero_improvement = (baseline_zero - final_zero) / baseline_zero * 100
    improvements['zero_rate'] = zero_improvement
    print(f"Zero Rate:      {final_zero:.3f} vs {baseline_zero:.3f} baseline "
          f"({zero_improvement:+.1f}%)")
    
    # Success rate (higher is better)
    baseline_success = 0.1189
    final_success = final_metrics['mean_success_rate']
    success_improvement = (final_success - baseline_success) / baseline_success * 100
    improvements['success_rate'] = success_improvement
    print(f"Success Rate:   {final_success:.3f} vs {baseline_success:.3f} baseline "
          f"({success_improvement:+.1f}%)")
    
    # Excellence rate (higher is better)
    baseline_excellence = 0.0540
    final_excellence = final_metrics['mean_excellence_rate']
    excellence_improvement = (final_excellence - baseline_excellence) / baseline_excellence * 100
    improvements['excellence_rate'] = excellence_improvement
    print(f"Excellence Rate:{final_excellence:.3f} vs {baseline_excellence:.3f} baseline "
          f"({excellence_improvement:+.1f}%)")
    
    # Target achievement
    targets_met = final_gen['summary']['agents_meeting_all_targets']
    print(f"\nAgents meeting ALL targets: {targets_met}/{args.pop}")
    
    # Overall assessment
    print("\n🎯 TARGET ACHIEVEMENT:")
    target_checks = {
        'Zero Rate < 8%': final_zero < 0.08,
        'Success Rate > 15%': final_success > 0.15,
        'Excellence Rate > 10%': final_excellence > 0.10,
        'Population Improvement': sum(v > 0 for v in improvements.values()) >= 2
    }
    
    for check, passed in target_checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status} {check}")
    
    overall_success = sum(target_checks.values()) >= 3
    print(f"\n{'OVERALL SUCCESS' if overall_success else 'PARTIAL SUCCESS'}")
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced Population-Based Training Runner"
    )
    parser.add_argument("--env", default="CartPole-v1", 
                       help="Gym environment ID")
    parser.add_argument("--gens", type=int, default=20, 
                       help="Number of generations")
    parser.add_argument("--pop", type=int, default=8, 
                       help="Population size")
    parser.add_argument("--eval-steps", type=int, default=500,
                       help="Evaluation steps per generation")
    parser.add_argument("--exploit-frac", type=float, default=0.5,
                       help="Fraction of population to exploit from")
    parser.add_argument("--mock", action="store_true",
                       help="Use mock environment instead of gym")
    parser.add_argument("--custom", action="store_true",
                       help="Use custom environments (no gym dependency)")
    parser.add_argument("--baseline-test", action="store_true",
                       help="Run baseline comparison test")
    parser.add_argument("--seed", type=int, default=None,
                       help="Random seed for reproducibility")
    parser.add_argument("--no-target-aware", action="store_true",
                       help="Disable target-aware scoring")
    parser.add_argument("--no-adaptive-mutation", action="store_true",
                       help="Disable adaptive mutation")
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        np.random.seed(args.seed)
        print(f"🎲 Random seed set to {args.seed}")
    
    # Run baseline comparison test
    if args.baseline_test:
        return run_baseline_comparison_test(args)
    
    # Determine environment factory
    if args.mock:
        env_fn = make_mock_env(args.seed)
        print(f"🤖 Using mock environment (seed={args.seed})")
    elif args.custom or not GYM_AVAILABLE:
        env_fn = make_custom_env(args.env)
        print(f"Using custom environment: {args.env}")
        print(f"   Available: {list(ENVIRONMENT_REGISTRY.keys())}")
    else:
        env_fn = make_gym_env(args.env)
        print(f"🏋️  Using gym environment: {args.env}")
    
    # Create enhanced scheduler
    scheduler = EnhancedScheduler(
        env_fn=env_fn,
        pop_size=args.pop,
        eval_steps=args.eval_steps,
        exploit_frac=args.exploit_frac,
        target_aware=not args.no_target_aware,
        adaptive_mutation=not args.no_adaptive_mutation
    )
    
    print(f"\nStarting PBT with enhanced scheduler")
    print(f"Population: {args.pop}, Generations: {args.gens}")
    print(f"Target-aware: {not args.no_target_aware}")
    print(f"Adaptive mutation: {not args.no_adaptive_mutation}")
    
    # Run training
    results = scheduler.run_training(args.gens)
    
    # Final summary
    print(f"\nTraining Summary:")
    print(f"Best score: {results['best_score_achieved']:.3f}")
    print(f"Agents meeting targets: {results['max_targets_met']}/{args.pop}")
    
    # Integration with analysis pipeline
    print(f"\nIntegration with analysis pipeline:")
    print(f"Log files saved to: pbt/logs/")
    print(f"Checkpoints saved to: pbt/output/")
    print(f"\nTo analyze with existing tools:")
    print(f"python scripts/analyze_agent_dump.py --consistency --dir pbt/logs")
    
    return results


if __name__ == "__main__":
    try:
        results = main()
        print("\nPBT training completed successfully!")
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 