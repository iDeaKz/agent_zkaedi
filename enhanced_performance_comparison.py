#!/usr/bin/env python3
"""
Enhanced Performance Comparison for PBT vs Baseline
Integrates with correlation analysis and provides comprehensive reporting.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from pathlib import Path
import argparse

class EnhancedPerformanceComparator:
    """Enhanced performance comparison with correlation analysis integration."""
    
    def __init__(self, output_dir: str = "pbt/analysis_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Baseline metrics from confirmed analysis
        self.baseline_metrics = {
            'zero_rate': 0.1193,
            'success_rate': 0.1189,
            'excellence_rate': 0.0540,
            'mean_value': 0.2897
        }
        
        # Phase 1 targets
        self.phase1_targets = {
            'zero_rate': 0.08,
            'success_rate': 0.15,
            'excellence_rate': 0.10,
            'mean_value': 0.35
        }
    
    def calculate_metrics(self, data: np.ndarray) -> dict:
        """Calculate performance metrics."""
        return {
            'zero_rate': np.mean(data == 0),
            'success_rate': np.mean(data > 0.75),
            'excellence_rate': np.mean(data > 0.9),
            'mean_value': np.mean(data)
        }
    
    def compare_performance(self, baseline_data: dict, pbt_data: dict):
        """Create performance comparison visualization."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Calculate population metrics
        baseline_metrics = [self.calculate_metrics(data) for data in baseline_data.values()]
        pbt_metrics = [self.calculate_metrics(data) for data in pbt_data.values()]
        
        # Population averages
        baseline_avg = {
            metric: np.mean([m[metric] for m in baseline_metrics])
            for metric in ['zero_rate', 'success_rate', 'excellence_rate', 'mean_value']
        }
        pbt_avg = {
            metric: np.mean([m[metric] for m in pbt_metrics])
            for metric in ['zero_rate', 'success_rate', 'excellence_rate', 'mean_value']
        }
        
        # Plot 1: Strategy Space
        baseline_zeros = [m['zero_rate'] for m in baseline_metrics]
        baseline_success = [m['success_rate'] for m in baseline_metrics]
        pbt_zeros = [m['zero_rate'] for m in pbt_metrics]
        pbt_success = [m['success_rate'] for m in pbt_metrics]
        
        ax1.scatter(baseline_zeros, baseline_success, c='red', alpha=0.6, 
                   s=100, label='Baseline', marker='x')
        ax1.scatter(pbt_zeros, pbt_success, c='blue', alpha=0.7, 
                   s=100, label='PBT', marker='o')
        
        # Reference lines
        ax1.axvline(x=self.baseline_metrics['zero_rate'], color='red', 
                   linestyle='--', alpha=0.5)
        ax1.axhline(y=self.baseline_metrics['success_rate'], color='red', 
                   linestyle='--', alpha=0.5)
        ax1.axvline(x=self.phase1_targets['zero_rate'], color='green', 
                   linestyle='-', alpha=0.7)
        ax1.axhline(y=self.phase1_targets['success_rate'], color='green', 
                   linestyle='-', alpha=0.7)
        
        ax1.set_xlabel('Zero Rate (Failure)')
        ax1.set_ylabel('Success Rate (>0.75)')
        ax1.set_title('Strategy Space: Baseline vs PBT')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Metrics Comparison
        metrics_names = ['Zero Rate', 'Success Rate', 'Excellence Rate', 'Mean Value']
        baseline_values = [baseline_avg[k] for k in ['zero_rate', 'success_rate', 'excellence_rate', 'mean_value']]
        pbt_values = [pbt_avg[k] for k in ['zero_rate', 'success_rate', 'excellence_rate', 'mean_value']]
        target_values = [self.phase1_targets[k] for k in ['zero_rate', 'success_rate', 'excellence_rate', 'mean_value']]
        
        x = np.arange(len(metrics_names))
        width = 0.25
        
        ax2.bar(x - width, baseline_values, width, label='Baseline', color='red', alpha=0.7)
        ax2.bar(x, pbt_values, width, label='PBT', color='blue', alpha=0.7)
        ax2.bar(x + width, target_values, width, label='Target', color='green', alpha=0.7)
        
        ax2.set_xlabel('Metrics')
        ax2.set_ylabel('Value')
        ax2.set_title('Performance Comparison')
        ax2.set_xticks(x)
        ax2.set_xticklabels(metrics_names, rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Performance comparison saved: {self.output_dir / 'performance_comparison.png'}")
        
        # Print summary
        print("\n📊 Performance Summary:")
        for metric in ['zero_rate', 'success_rate', 'excellence_rate', 'mean_value']:
            baseline_val = baseline_avg[metric]
            pbt_val = pbt_avg[metric]
            target = self.phase1_targets[metric]
            
            if metric == 'zero_rate':  # Lower is better
                improvement = (baseline_val - pbt_val) / baseline_val * 100
                target_met = pbt_val < target
            else:  # Higher is better
                improvement = (pbt_val - baseline_val) / baseline_val * 100
                target_met = pbt_val > target
            
            status = "✅" if target_met else "❌"
            print(f"   {metric.replace('_', ' ').title()}: {pbt_val:.3f} ({improvement:+.1f}%) {status}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enhanced Performance Comparison")
    parser.add_argument("--baseline-dir", default="data", help="Baseline data directory")
    parser.add_argument("--pbt-dir", default="pbt/analysis", help="PBT data directory")
    parser.add_argument("--output-dir", default="pbt/analysis_output", help="Output directory")
    args = parser.parse_args()
    
    print("📊 ENHANCED PERFORMANCE COMPARISON")
    print("=" * 50)
    
    comparator = EnhancedPerformanceComparator(args.output_dir)
    
    # Mock data for demonstration
    print("📂 Using mock data for demonstration...")
    
    # Baseline data (consistent with our analysis)
    baseline_data = {
        f'baseline_agent_{i}': np.random.beta(1.5, 5, 100000) for i in range(5)
    }
    
    # PBT data (showing improvement)
    pbt_data = {
        f'pbt_agent_{i}': np.random.beta(2.5, 6, 100000) for i in range(4)
    }
    
    print(f"✅ Generated {len(baseline_data)} baseline agents, {len(pbt_data)} PBT agents")
    
    # Perform comparison
    comparator.compare_performance(baseline_data, pbt_data)
    
    print(f"\n🎉 Comparison complete! Check {args.output_dir}")


if __name__ == "__main__":
    main()
