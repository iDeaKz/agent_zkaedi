"""
RL Agent abstraction for Population-Based Training.
Enhanced with correlation analysis insights from multi-agent consistency study.

Based on findings:
- Zero Rate vs Excellence Rate: -0.334585 (target zero rate reduction)
- Excellence Rate vs Mean Value: 0.617964 (excellence drives performance)
- Extremely high consistency: Need diversity to break suboptimal equilibrium
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any
import json

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


@dataclass
class AgentConfig:
    """
    Hyper-parameters subject to PBT evolution.
    Enhanced with reward shaping and exploration parameters from our analysis.
    """
    epsilon: float              # Exploration rate (target: 0.2 vs baseline 0.1)
    lr: float                  # Learning rate
    discount: float            # Discount factor
    reward_shaping: float      # Reward shaping scale (from our wrapper)
    partial_reward: float      # Intermediate reward for partial progress
    near_success_reward: float # Reward for near-success states
    entropy_bonus: float       # Entropy bonus for exploration diversity
    
    @classmethod
    def random_init(cls) -> "AgentConfig":
        """
        Initialize with diverse hyperparameters to break agent convergence.
        Ranges based on our correlation analysis and research recommendations.
        """
        rng = np.random.default_rng()
        return cls(
            # Enhanced exploration (baseline agents had ~0.1, we target 0.2+)
            epsilon=rng.uniform(0.15, 0.35),
            lr=float(rng.uniform(1e-4, 1e-2)),
            discount=float(rng.uniform(0.90, 0.99)),
            
            # Reward shaping parameters (from our wrapper analysis)
            reward_shaping=float(rng.uniform(0.5, 2.0)),
            partial_reward=float(rng.choice([0.05, 0.1, 0.15, 0.2])),
            near_success_reward=float(rng.choice([0.1, 0.2, 0.25, 0.3])),
            
            # Diversity enhancement
            entropy_bonus=float(rng.uniform(0.001, 0.05)),
        )
    
    @classmethod
    def from_baseline_analysis(cls, agent_id: int = 0) -> "AgentConfig":
        """
        Create config based on baseline analysis insights.
        Each agent gets slightly different parameters to encourage diversity.
        """
        base_configs = [
            # Conservative agent (low exploration, high shaping)
            cls(epsilon=0.15, lr=1e-3, discount=0.95, reward_shaping=1.5,
                partial_reward=0.1, near_success_reward=0.2, entropy_bonus=0.01),
            
            # Balanced agent (moderate exploration and shaping)
            cls(epsilon=0.2, lr=5e-4, discount=0.97, reward_shaping=1.0,
                partial_reward=0.15, near_success_reward=0.25, entropy_bonus=0.02),
            
            # Aggressive agent (high exploration, lower shaping)
            cls(epsilon=0.3, lr=2e-3, discount=0.93, reward_shaping=0.8,
                partial_reward=0.05, near_success_reward=0.15, entropy_bonus=0.03),
            
            # Curiosity-driven agent (high entropy bonus)
            cls(epsilon=0.25, lr=1e-3, discount=0.96, reward_shaping=1.2,
                partial_reward=0.2, near_success_reward=0.3, entropy_bonus=0.05),
        ]
        
        return base_configs[agent_id % len(base_configs)]

    def mutate(self, sigma: float = 0.2) -> None:
        """
        Gaussian or multiplicative jitter to encourage exploration.
        Enhanced mutation strategy to maintain diversity.
        """
        g = np.random.default_rng()
        
        # Exploration mutation (key for breaking suboptimal equilibrium)
        self.epsilon = np.clip(self.epsilon * g.uniform(0.8, 1.2), 0.05, 0.5)
        
        # Learning rate mutation
        self.lr = float(np.clip(self.lr * g.uniform(0.5, 1.5), 1e-5, 1e-1))
        
        # Discount factor mutation
        self.discount = float(np.clip(self.discount + g.normal(0, 0.01), 0.80, 0.999))
        
        # Reward shaping mutations (critical for zero rate reduction)
        self.reward_shaping = float(np.clip(self.reward_shaping * g.uniform(0.7, 1.3), 0.1, 3.0))
        self.partial_reward = float(np.clip(self.partial_reward * g.uniform(0.8, 1.2), 0.01, 0.3))
        self.near_success_reward = float(np.clip(self.near_success_reward * g.uniform(0.8, 1.2), 0.05, 0.5))
        
        # Entropy bonus mutation (for diversity)
        self.entropy_bonus = float(np.clip(self.entropy_bonus * g.uniform(0.5, 2.0), 0.001, 0.1))

    def get_performance_prediction(self) -> Dict[str, float]:
        """
        Predict performance based on our correlation analysis.
        Returns expected zero rate, success rate, etc.
        """
        # Based on correlation analysis:
        # Higher exploration (epsilon) should reduce zero rate
        # Higher reward shaping should improve mean value
        # Higher entropy should increase diversity
        
        predicted_zero_rate = max(0.02, 0.12 - (self.epsilon - 0.1) * 0.3 - self.reward_shaping * 0.02)
        predicted_success_rate = min(0.35, 0.12 + self.reward_shaping * 0.05 + self.epsilon * 0.1)
        predicted_mean_value = min(1.0, 0.29 + self.reward_shaping * 0.1 + self.partial_reward * 0.5)
        
        return {
            "predicted_zero_rate": predicted_zero_rate,
            "predicted_success_rate": predicted_success_rate,
            "predicted_mean_value": predicted_mean_value,
            "diversity_score": self.epsilon * self.entropy_bonus
        }

    def meets_targets(self) -> Dict[str, bool]:
        """
        Check if configuration is likely to meet our targets:
        - Zero rate <8% (down from 11.93%)
        - Success rate >15% (up from 11.89%)
        - Mean value >0.35 (up from 0.2897)
        """
        pred = self.get_performance_prediction()
        return {
            "zero_rate_target": pred["predicted_zero_rate"] < 0.08,
            "success_rate_target": pred["predicted_success_rate"] > 0.15,
            "mean_value_target": pred["predicted_mean_value"] > 0.35,
            "diversity_target": pred["diversity_score"] > 0.01
        }

    # ---- Serialization helpers ------------------------------------------------
    def asdict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self, path: Path) -> None:
        """Save configuration to JSON file."""
        path.write_text(json.dumps(self.asdict(), indent=2))
    
    @classmethod
    def from_json(cls, path: Path) -> "AgentConfig":
        """Load configuration from JSON file."""
        data = json.loads(path.read_text())
        return cls(**data)

    def __str__(self) -> str:
        """Human-readable representation."""
        pred = self.get_performance_prediction()
        targets = self.meets_targets()
        targets_met = sum(targets.values())
        
        return (f"AgentConfig(ε={self.epsilon:.3f}, lr={self.lr:.1e}, "
                f"shaping={self.reward_shaping:.2f}, "
                f"pred_zero={pred['predicted_zero_rate']:.3f}, "
                f"targets_met={targets_met}/4)")


if __name__ == "__main__":
    # Test the enhanced agent configuration
    print("🧪 Testing Enhanced Agent Configuration")
    print("=" * 50)
    
    # Test random initialization
    print("\n🎲 Random Initialization:")
    for i in range(3):
        config = AgentConfig.random_init()
        print(f"Agent {i}: {config}")
    
    # Test baseline-informed initialization
    print("\n📊 Baseline-Informed Initialization:")
    for i in range(4):
        config = AgentConfig.from_baseline_analysis(i)
        print(f"Agent {i}: {config}")
    
    # Test mutation
    print("\n🧬 Mutation Example:")
    config = AgentConfig.from_baseline_analysis(0)
    print(f"Original: {config}")
    config.mutate()
    print(f"Mutated:  {config}")
    
    print("\n✅ Enhanced Agent Configuration Ready!") 