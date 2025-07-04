"""
Enhanced trainer that integrates with reward shaping and exploration strategies.
Designed to break the suboptimal equilibrium identified in baseline analysis.

Integration points:
- Uses our EnhancedShapedRewardEnv wrapper
- Implements exploration strategies from exploration_enhancement.py
- Tracks metrics aligned with our performance targets
"""
from __future__ import annotations
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
import sys

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from reward_shaping_wrapper import EnhancedShapedRewardEnv
    from exploration_enhancement import ExplorationManager
except ImportError:
    # Fallback for testing without full environment
    EnhancedShapedRewardEnv = None
    ExplorationManager = None

from agent import AgentConfig

# Handle relative imports
try:
    from .environments import BaseEnvironment, make_environment, MockEnvironment
except ImportError:
    from environments import BaseEnvironment, make_environment, MockEnvironment


class SimpleMLP(torch.nn.Module):
    """
    Simple Multi-Layer Perceptron for RL policy.
    Enhanced with dropout for regularization and better generalization.
    """
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 64) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(state_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.1),  # Regularization
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.1),
            torch.nn.Linear(hidden_dim, action_dim),
        )
        
        # Initialize weights for better learning
        for layer in self.net:
            if isinstance(layer, torch.nn.Linear):
                torch.nn.init.xavier_uniform_(layer.weight)
                torch.nn.init.zeros_(layer.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class EnhancedTrainer:
    """
    Enhanced trainer that integrates reward shaping and exploration strategies.
    Tracks metrics aligned with our correlation analysis targets.
    """
    
    def __init__(self, env, config: AgentConfig, agent_id: int = 0) -> None:
        self.base_env = env
        self.cfg = config
        self.agent_id = agent_id
        
        # Wrap environment with our enhanced reward shaping
        if EnhancedShapedRewardEnv is not None:
            self.env = EnhancedShapedRewardEnv(
                env=env,
                environment_type="generic",  # Can be customized
                partial_reward=config.partial_reward,
                near_success_reward=config.near_success_reward,
                shaping_scale=config.reward_shaping,
                log_metrics=False  # Disable per-step logging for performance
            )
        else:
            self.env = env
            
        # Initialize model and optimizer
        if hasattr(env.observation_space, 'shape'):
            state_dim = env.observation_space.shape[0]
        else:
            state_dim = 4  # Default fallback
            
        if hasattr(env.action_space, 'n'):
            action_dim = env.action_space.n
        else:
            action_dim = 2  # Default fallback
            
        self.model = SimpleMLP(state_dim, action_dim)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.cfg.lr)
        
        # Enhanced exploration manager
        if ExplorationManager is not None:
            self.explorer = ExplorationManager(
                strategy="epsilon_greedy",
                epsilon=config.epsilon
            )
        else:
            self.explorer = None
            
        # Metrics tracking (aligned with our analysis targets)
        self.reset_metrics()
        
    def reset_metrics(self) -> None:
        """Reset metrics for new training period."""
        self.episode_rewards = []
        self.zero_episodes = 0
        self.success_episodes = 0  # >0.75
        self.excellence_episodes = 0  # >0.9
        self.total_episodes = 0
        self.partial_progress_count = 0
        self.near_success_count = 0
        
    def train_steps(self, n_steps: int) -> float:
        """
        Run n_steps and return performance metrics.
        Enhanced with our correlation analysis insights.
        """
        total_reward = 0.0
        state = self.env.reset()
        episode_reward = 0.0
        step_count = 0
        
        for step in range(n_steps):
            # Enhanced action selection
            action = self._select_action(state, step)
            
            # Take step in environment
            next_state, reward, done, info = self.env.step(action)
            episode_reward += reward
            total_reward += reward
            
            # Track shaping metrics if available
            if isinstance(info, dict):
                if info.get('intermediate_reward', 0) > 0:
                    if info.get('intermediate_reward') == self.cfg.partial_reward:
                        self.partial_progress_count += 1
                    elif info.get('intermediate_reward') == self.cfg.near_success_reward:
                        self.near_success_count += 1
            
            # Simple TD learning update
            self._update_model(state, action, reward, next_state, done)
            
            # Handle episode completion
            if done:
                self._record_episode(episode_reward)
                state = self.env.reset()
                episode_reward = 0.0
                step_count = 0
            else:
                state = next_state
                step_count += 1
        
        return total_reward
    
    def _select_action(self, state: np.ndarray, step: int) -> int:
        """Enhanced action selection with exploration strategies."""
        if self.explorer is not None:
            # Use our enhanced exploration manager
            def policy_fn(s):
                with torch.no_grad():
                    logits = self.model(torch.as_tensor(s, dtype=torch.float32))
                    return logits.numpy()
            
            # Mock action space for exploration manager
            class MockActionSpace:
                def __init__(self, n):
                    self.n = n
            
            mock_space = MockActionSpace(self.model.net[-1].out_features)
            action = self.explorer.choose_action(state, policy_fn, mock_space)
        else:
            # Fallback epsilon-greedy
            if np.random.rand() < self.cfg.epsilon:
                action = np.random.randint(0, self.model.net[-1].out_features)
            else:
                with torch.no_grad():
                    logits = self.model(torch.as_tensor(state, dtype=torch.float32))
                    action = int(torch.argmax(logits).item())
        
        return action
    
    def _update_model(self, state: np.ndarray, action: int, reward: float, 
                     next_state: np.ndarray, done: bool) -> None:
        """Simple TD learning update with entropy bonus."""
        state_tensor = torch.as_tensor(state, dtype=torch.float32)
        next_state_tensor = torch.as_tensor(next_state, dtype=torch.float32)
        
        # Current Q-value
        current_q = self.model(state_tensor)[action]
        
        # Target Q-value
        with torch.no_grad():
            if done:
                target_q = reward
            else:
                next_q_values = self.model(next_state_tensor)
                target_q = reward + self.cfg.discount * torch.max(next_q_values).item()
        
        # Add entropy bonus for exploration
        if self.cfg.entropy_bonus > 0:
            with torch.no_grad():
                logits = self.model(state_tensor)
                probs = torch.softmax(logits, dim=0)
                entropy = -torch.sum(probs * torch.log(probs + 1e-8))
                target_q += self.cfg.entropy_bonus * entropy.item()
        
        # Compute loss and update
        loss = (current_q - target_q).pow(2)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def _record_episode(self, episode_reward: float) -> None:
        """Record episode metrics aligned with our analysis targets."""
        self.episode_rewards.append(episode_reward)
        self.total_episodes += 1
        
        # Track zero episodes (target: <8% from 11.93%)
        if episode_reward == 0.0:
            self.zero_episodes += 1
            
        # Track success episodes (target: >15% from 11.89%)
        if episode_reward > 0.75:
            self.success_episodes += 1
            
        # Track excellence episodes (target: >10% from 5.40%)
        if episode_reward > 0.9:
            self.excellence_episodes += 1
    
    def get_metrics(self) -> Dict[str, float]:
        """
        Get comprehensive metrics aligned with our correlation analysis.
        Returns metrics comparable to baseline analysis.
        """
        if self.total_episodes == 0:
            return {
                "zero_rate": 0.0,
                "success_rate": 0.0,
                "excellence_rate": 0.0,
                "mean_value": 0.0,
                "total_episodes": 0,
                "partial_progress_count": 0,
                "near_success_count": 0
            }
        
        metrics = {
            "zero_rate": self.zero_episodes / self.total_episodes,
            "success_rate": self.success_episodes / self.total_episodes,
            "excellence_rate": self.excellence_episodes / self.total_episodes,
            "mean_value": np.mean(self.episode_rewards) if self.episode_rewards else 0.0,
            "std_value": np.std(self.episode_rewards) if self.episode_rewards else 0.0,
            "total_episodes": self.total_episodes,
            "partial_progress_count": self.partial_progress_count,
            "near_success_count": self.near_success_count
        }
        
        # Add target achievement flags
        metrics.update({
            "zero_rate_target_met": metrics["zero_rate"] < 0.08,
            "success_rate_target_met": metrics["success_rate"] > 0.15,
            "excellence_rate_target_met": metrics["excellence_rate"] > 0.10,
            "mean_value_target_met": metrics["mean_value"] > 0.35
        })
        
        return metrics
    
    def get_performance_score(self) -> float:
        """
        Calculate overall performance score for PBT ranking.
        Weighted by our correlation analysis insights.
        """
        metrics = self.get_metrics()
        
        if metrics["total_episodes"] == 0:
            return 0.0
        
        # Weighted scoring based on correlation analysis:
        # - Excellence rate has strong correlation with mean value (0.617964)
        # - Zero rate has negative correlation with excellence (-0.334585)
        # - Success rate drives overall performance
        
        score = (
            metrics["mean_value"] * 0.4 +  # Primary performance indicator
            metrics["success_rate"] * 0.3 +  # Success rate importance
            metrics["excellence_rate"] * 0.2 +  # Excellence correlation
            (1.0 - metrics["zero_rate"]) * 0.1  # Zero rate penalty
        )
        
        return float(score)
    
    def save_checkpoint(self, path: Path) -> None:
        """Save model checkpoint."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.cfg.asdict(),
            'metrics': self.get_metrics()
        }, path)
    
    def load_checkpoint(self, path: Path) -> None:
        """Load model checkpoint."""
        checkpoint = torch.load(path)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])


# Backward compatibility with original scaffold
class Trainer(EnhancedTrainer):
    """Backward compatibility wrapper for original scaffold."""
    
    def __init__(self, env, config: AgentConfig) -> None:
        # Convert old config format if needed
        if not hasattr(config, 'partial_reward'):
            # Add missing attributes with defaults
            config.partial_reward = 0.1
            config.near_success_reward = 0.2
            config.entropy_bonus = 0.01
            
        super().__init__(env, config)
    
    def train_steps(self, n_steps: int) -> float:
        """Original interface - returns total reward."""
        return super().train_steps(n_steps)


if __name__ == "__main__":
    # Test the enhanced trainer
    print("🧪 Testing Enhanced Trainer")
    print("=" * 40)
    
    # Test agent configuration
    config = AgentConfig.from_baseline_analysis(0)
    print(f"Test config: {config}")
    
    # Mock environment for testing
    # Use our custom MockEnvironment instead of inline class
    def make_mock_env():
        return MockEnvironment(state_dim=4, action_dim=2, reward_type="baseline_calibrated")
    
    # Test trainer
    env = make_mock_env()
    trainer = EnhancedTrainer(env, config)
    
    # Run short training
    reward = trainer.train_steps(100)
    metrics = trainer.get_metrics()
    
    print(f"Training reward: {reward:.3f}")
    print(f"Performance score: {trainer.get_performance_score():.3f}")
    print("Metrics:", {k: f"{v:.3f}" if isinstance(v, float) else v 
                      for k, v in metrics.items()})
    
    print("\n✅ Enhanced Trainer Ready!") 