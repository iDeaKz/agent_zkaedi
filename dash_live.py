"""
Enhanced Live Dashboard for Population-Based Training
Integrates with our correlation analysis and performance targets.

Features:
- Real-time PBT monitoring
- Target achievement tracking
- Correlation analysis visualization
- Performance trend analysis
- Agent diversity metrics

Usage:
    streamlit run pbt/dash_live.py
    # or
    python pbt/dash_live.py  # fallback matplotlib version
"""
import json
import time
import glob
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

# Try to import streamlit
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("⚠️  Streamlit not available, using matplotlib fallback")

# Import our modules
try:
    from agent import AgentConfig
except ImportError:
    AgentConfig = None


class PBTDashboard:
    """Enhanced dashboard for PBT monitoring."""
    
    def __init__(self, log_dir: str = "pbt/logs"):
        self.log_dir = Path(log_dir)
        self.baseline_metrics = {
            'zero_rate': 0.1193,
            'success_rate': 0.1189,
            'excellence_rate': 0.0540,
            'mean_value': 0.2897
        }
        self.targets = {
            'zero_rate': 0.08,
            'success_rate': 0.15,
            'excellence_rate': 0.10,
            'mean_value': 0.35
        }
        
    def load_latest_data(self) -> Optional[Dict[str, Any]]:
        """Load the latest generation data."""
        if not self.log_dir.exists():
            return None
            
        gen_files = sorted(self.log_dir.glob("gen_*.json"))
        if not gen_files:
            return None
            
        latest_file = gen_files[-1]
        try:
            with open(latest_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {latest_file}: {e}")
            return None
    
    def load_all_generations(self) -> List[Dict[str, Any]]:
        """Load all generation data."""
        if not self.log_dir.exists():
            return []
            
        gen_files = sorted(self.log_dir.glob("gen_*.json"))
        generations = []
        
        for gen_file in gen_files:
            try:
                with open(gen_file) as f:
                    data = json.load(f)
                    generations.append(data)
            except Exception as e:
                print(f"Error loading {gen_file}: {e}")
                continue
                
        return generations
    
    def create_performance_plot(self, generations: List[Dict]) -> plt.Figure:
        """Create performance trend plot."""
        if not generations:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            return fig
            
        # Extract data
        gen_nums = [g['generation'] for g in generations]
        best_scores = [g['summary']['best_score'] for g in generations]
        mean_scores = [g['summary']['mean_score'] for g in generations]
        targets_met = [g['summary']['agents_meeting_all_targets'] for g in generations]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Performance scores
        ax1.plot(gen_nums, best_scores, 'g-', label='Best Score', linewidth=2)
        ax1.plot(gen_nums, mean_scores, 'b-', label='Mean Score', linewidth=2)
        ax1.fill_between(gen_nums, best_scores, mean_scores, alpha=0.3)
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Performance Score')
        ax1.set_title('Performance Evolution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Target achievement
        ax2.bar(gen_nums, targets_met, alpha=0.7, color='orange')
        ax2.set_xlabel('Generation')
        ax2.set_ylabel('Agents Meeting All Targets')
        ax2.set_title('Target Achievement Progress')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_metrics_comparison_plot(self, generations: List[Dict]) -> plt.Figure:
        """Create metrics comparison vs baseline."""
        if not generations:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            return fig
            
        latest = generations[-1]
        metrics = latest['summary']['population_metrics']
        
        # Prepare data
        metric_names = ['Zero Rate', 'Success Rate', 'Excellence Rate']
        current_values = [
            metrics['mean_zero_rate'],
            metrics['mean_success_rate'], 
            metrics['mean_excellence_rate']
        ]
        baseline_values = [
            self.baseline_metrics['zero_rate'],
            self.baseline_metrics['success_rate'],
            self.baseline_metrics['excellence_rate']
        ]
        target_values = [
            self.targets['zero_rate'],
            self.targets['success_rate'],
            self.targets['excellence_rate']
        ]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(metric_names))
        width = 0.25
        
        bars1 = ax.bar(x - width, baseline_values, width, label='Baseline', color='red', alpha=0.7)
        bars2 = ax.bar(x, current_values, width, label='Current', color='blue', alpha=0.7)
        bars3 = ax.bar(x + width, target_values, width, label='Target', color='green', alpha=0.7)
        
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Rate')
        ax.set_title('Performance Metrics: Current vs Baseline vs Target')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.3f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        return fig
    
    def create_agent_diversity_plot(self, latest_data: Dict) -> plt.Figure:
        """Create agent diversity visualization."""
        if not latest_data or 'agents' not in latest_data:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No agent data available', ha='center', va='center')
            return fig
            
        agents = latest_data['agents']
        
        # Extract hyperparameters
        epsilons = [agent.get('epsilon', 0) for agent in agents]
        learning_rates = [agent.get('lr', 0) for agent in agents]
        reward_shapings = [agent.get('reward_shaping', 0) for agent in agents]
        scores = [agent.get('score', 0) for agent in agents]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Epsilon distribution
        ax1.hist(epsilons, bins=10, alpha=0.7, color='blue')
        ax1.set_xlabel('Epsilon (Exploration Rate)')
        ax1.set_ylabel('Count')
        ax1.set_title('Exploration Rate Distribution')
        ax1.grid(True, alpha=0.3)
        
        # Learning rate distribution
        ax2.hist(learning_rates, bins=10, alpha=0.7, color='green')
        ax2.set_xlabel('Learning Rate')
        ax2.set_ylabel('Count')
        ax2.set_title('Learning Rate Distribution')
        ax2.set_xscale('log')
        ax2.grid(True, alpha=0.3)
        
        # Reward shaping vs performance
        ax3.scatter(reward_shapings, scores, alpha=0.7, color='red')
        ax3.set_xlabel('Reward Shaping Scale')
        ax3.set_ylabel('Performance Score')
        ax3.set_title('Reward Shaping vs Performance')
        ax3.grid(True, alpha=0.3)
        
        # Epsilon vs performance
        ax4.scatter(epsilons, scores, alpha=0.7, color='purple')
        ax4.set_xlabel('Epsilon (Exploration Rate)')
        ax4.set_ylabel('Performance Score')
        ax4.set_title('Exploration vs Performance')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig


def run_streamlit_dashboard():
    """Run the Streamlit version of the dashboard."""
    st.set_page_config(
        page_title="🧬 PBT Dashboard",
        page_icon="🧬",
        layout="wide"
    )
    
    st.title("🧬 Population-Based Training Dashboard")
    st.markdown("Real-time monitoring of PBT with correlation analysis integration")
    
    dashboard = PBTDashboard()
    
    # Sidebar controls
    st.sidebar.header("Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 1, 30, 5)
    
    if st.sidebar.button("Manual Refresh") or auto_refresh:
        # Load data
        latest_data = dashboard.load_latest_data()
        all_generations = dashboard.load_all_generations()
        
        if not latest_data:
            st.warning("⚠️ No PBT data found. Start training with: `python pbt/pbt_runner.py`")
            st.stop()
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Generation", 
                latest_data['generation'],
                delta=None
            )
        
        with col2:
            best_score = latest_data['summary']['best_score']
            st.metric(
                "Best Score", 
                f"{best_score:.3f}",
                delta=None
            )
        
        with col3:
            targets_met = latest_data['summary']['agents_meeting_all_targets']
            pop_size = latest_data['population_size']
            st.metric(
                "Targets Met", 
                f"{targets_met}/{pop_size}",
                delta=None
            )
        
        with col4:
            zero_rate = latest_data['summary']['population_metrics']['mean_zero_rate']
            st.metric(
                "Zero Rate", 
                f"{zero_rate:.3f}",
                delta=f"{(dashboard.baseline_metrics['zero_rate'] - zero_rate):.3f}"
            )
        
        # Performance plots
        st.subheader("📈 Performance Trends")
        fig1 = dashboard.create_performance_plot(all_generations)
        st.pyplot(fig1)
        
        # Metrics comparison
        st.subheader("📊 Metrics vs Baseline")
        fig2 = dashboard.create_metrics_comparison_plot(all_generations)
        st.pyplot(fig2)
        
        # Agent diversity
        st.subheader("🎯 Agent Diversity")
        fig3 = dashboard.create_agent_diversity_plot(latest_data)
        st.pyplot(fig3)
        
        # Detailed metrics table
        st.subheader("📋 Detailed Metrics")
        metrics_df = pd.DataFrame([
            {
                'Metric': 'Zero Rate',
                'Current': latest_data['summary']['population_metrics']['mean_zero_rate'],
                'Baseline': dashboard.baseline_metrics['zero_rate'],
                'Target': dashboard.targets['zero_rate'],
                'Target Met': latest_data['summary']['population_metrics']['mean_zero_rate'] < dashboard.targets['zero_rate']
            },
            {
                'Metric': 'Success Rate',
                'Current': latest_data['summary']['population_metrics']['mean_success_rate'],
                'Baseline': dashboard.baseline_metrics['success_rate'],
                'Target': dashboard.targets['success_rate'],
                'Target Met': latest_data['summary']['population_metrics']['mean_success_rate'] > dashboard.targets['success_rate']
            },
            {
                'Metric': 'Excellence Rate',
                'Current': latest_data['summary']['population_metrics']['mean_excellence_rate'],
                'Baseline': dashboard.baseline_metrics['excellence_rate'],
                'Target': dashboard.targets['excellence_rate'],
                'Target Met': latest_data['summary']['population_metrics']['mean_excellence_rate'] > dashboard.targets['excellence_rate']
            }
        ])
        
        st.dataframe(metrics_df, use_container_width=True)
        
        # Agent details
        st.subheader("🤖 Agent Details")
        agents_df = pd.DataFrame(latest_data['agents'])
        st.dataframe(agents_df, use_container_width=True)
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(refresh_interval)
            st.experimental_rerun()


def run_matplotlib_dashboard():
    """Run the matplotlib fallback version."""
    print("🧬 PBT Dashboard (Matplotlib version)")
    print("Press Ctrl+C to exit")
    
    dashboard = PBTDashboard()
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    plt.ion()
    
    def update_plots():
        """Update all plots."""
        for ax in axes.flat:
            ax.clear()
        
        # Load data
        latest_data = dashboard.load_latest_data()
        all_generations = dashboard.load_all_generations()
        
        if not latest_data:
            axes[0, 0].text(0.5, 0.5, 'No PBT data found\nStart training first', 
                           ha='center', va='center')
            return
        
        # Performance trends
        if all_generations:
            gen_nums = [g['generation'] for g in all_generations]
            best_scores = [g['summary']['best_score'] for g in all_generations]
            mean_scores = [g['summary']['mean_score'] for g in all_generations]
            
            axes[0, 0].plot(gen_nums, best_scores, 'g-', label='Best', linewidth=2)
            axes[0, 0].plot(gen_nums, mean_scores, 'b-', label='Mean', linewidth=2)
            axes[0, 0].set_title('Performance Evolution')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
        
        # Metrics comparison
        metrics = latest_data['summary']['population_metrics']
        metric_names = ['Zero\nRate', 'Success\nRate', 'Excellence\nRate']
        current_values = [
            metrics['mean_zero_rate'],
            metrics['mean_success_rate'],
            metrics['mean_excellence_rate']
        ]
        baseline_values = [
            dashboard.baseline_metrics['zero_rate'],
            dashboard.baseline_metrics['success_rate'],
            dashboard.baseline_metrics['excellence_rate']
        ]
        
        x = np.arange(len(metric_names))
        width = 0.35
        
        axes[0, 1].bar(x - width/2, baseline_values, width, label='Baseline', alpha=0.7)
        axes[0, 1].bar(x + width/2, current_values, width, label='Current', alpha=0.7)
        axes[0, 1].set_title('Metrics vs Baseline')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(metric_names)
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Agent diversity
        if 'agents' in latest_data:
            agents = latest_data['agents']
            epsilons = [agent.get('epsilon', 0) for agent in agents]
            scores = [agent.get('score', 0) for agent in agents]
            
            axes[1, 0].scatter(epsilons, scores, alpha=0.7)
            axes[1, 0].set_xlabel('Epsilon')
            axes[1, 0].set_ylabel('Score')
            axes[1, 0].set_title('Exploration vs Performance')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Target achievement
        if all_generations:
            targets_met = [g['summary']['agents_meeting_all_targets'] for g in all_generations]
            axes[1, 1].bar(gen_nums, targets_met, alpha=0.7)
            axes[1, 1].set_xlabel('Generation')
            axes[1, 1].set_ylabel('Agents Meeting Targets')
            axes[1, 1].set_title('Target Achievement')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.draw()
        
        # Print summary
        print(f"\nGen {latest_data['generation']}: "
              f"Best={latest_data['summary']['best_score']:.3f}, "
              f"Targets={latest_data['summary']['agents_meeting_all_targets']}/{latest_data['population_size']}")
    
    try:
        while True:
            update_plots()
            plt.pause(5)  # Update every 5 seconds
    except KeyboardInterrupt:
        print("\nDashboard stopped")
    finally:
        plt.ioff()
        plt.close('all')


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--matplotlib":
        run_matplotlib_dashboard()
    elif STREAMLIT_AVAILABLE:
        run_streamlit_dashboard()
    else:
        print("Running matplotlib fallback dashboard...")
        run_matplotlib_dashboard()


if __name__ == "__main__":
    main() 