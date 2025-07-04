#!/usr/bin/env python3
"""
Enhanced PBT Results Visualization
Analyzes Population-Based Training results with correlation insights integration.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import json
from pathlib import Path
import argparse

class PBTResultsVisualizer:
    """Comprehensive PBT results visualization."""
    
    def __init__(self, output_dir: str = "pbt/visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Baseline metrics from our analysis
        self.baseline_metrics = {
            'zero_rate': 0.1193,
            'success_rate': 0.1189,
            'excellence_rate': 0.0540,
            'mean_value': 0.2897
        }
        
        # Target metrics
        self.targets = {
            'zero_rate': 0.08,
            'success_rate': 0.15,
            'excellence_rate': 0.10,
            'mean_value': 0.35
        }
    
    def calculate_metrics(self, data: np.ndarray) -> dict:
        """Calculate performance metrics for agent data."""
        return {
            'zero_rate': np.mean(data == 0),
            'success_rate': np.mean(data > 0.75),
            'excellence_rate': np.mean(data > 0.9),
            'mean_value': np.mean(data)
        }
    
    def plot_basic_comparison(self, pbt_data: dict):
        """Create basic comparison plot."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Calculate metrics for all agents
        metrics = []
        for agent_id, data in pbt_data['agents'].items():
            agent_metrics = self.calculate_metrics(data)
            metrics.append(agent_metrics)
        
        # Plot zero rate vs success rate
        zero_rates = [m['zero_rate'] for m in metrics]
        success_rates = [m['success_rate'] for m in metrics]
        
        ax.scatter(zero_rates, success_rates, s=100, alpha=0.7, label='PBT Agents')
        
        # Reference lines
        ax.axvline(x=self.baseline_metrics['zero_rate'], color='red', 
                  linestyle='--', alpha=0.7, label='Baseline Zero Rate')
        ax.axhline(y=self.baseline_metrics['success_rate'], color='red', 
                  linestyle='--', alpha=0.7, label='Baseline Success Rate')
        ax.axvline(x=self.targets['zero_rate'], color='green', 
                  linestyle='-', alpha=0.7, label='Target Zero Rate')
        ax.axhline(y=self.targets['success_rate'], color='green', 
                  linestyle='-', alpha=0.7, label='Target Success Rate')
        
        ax.set_xlabel('Zero Rate (Failure)')
        ax.set_ylabel('Success Rate (>0.75)')
        ax.set_title('PBT Strategy Space Analysis')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'pbt_strategy_space.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Strategy space plot saved: {self.output_dir / 'pbt_strategy_space.png'}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PBT Results Visualization")
    parser.add_argument("--pbt-dir", required=True, help="Directory with PBT agent data")
    parser.add_argument("--output-dir", default="pbt/visualizations", help="Output directory")
    args = parser.parse_args()
    
    print("🎨 PBT RESULTS VISUALIZATION")
    print("=" * 50)
    
    visualizer = PBTResultsVisualizer(args.output_dir)
    
    # Mock data for testing (replace with actual data loading)
    pbt_data = {
        'agents': {
            'agent_0': np.random.beta(2, 8, 1000),  # Simulates improved performance
            'agent_1': np.random.beta(3, 7, 1000),
            'agent_2': np.random.beta(2.5, 7.5, 1000),
            'agent_3': np.random.beta(3.5, 6.5, 1000)
        }
    }
    
    visualizer.plot_basic_comparison(pbt_data)
    print("🎉 Basic visualization complete!")

if __name__ == "__main__":
    main()
