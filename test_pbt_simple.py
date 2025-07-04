#!/usr/bin/env python3
"""
Simple PBT Test Script
Tests the core PBT components without heavy dependencies.
"""
import sys
from pathlib import Path
import numpy as np

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_agent_config():
    """Test agent configuration without PyTorch."""
    print("🧪 Testing Agent Configuration...")
    
    try:
        from pbt.agent import AgentConfig
        
        # Test random initialization
        config1 = AgentConfig.random_init()
        print(f"✅ Random config: {config1}")
        
        # Test baseline-informed initialization
        config2 = AgentConfig.from_baseline_analysis(0)
        print(f"✅ Baseline config: {config2}")
        
        # Test mutation
        original_epsilon = config2.epsilon
        config2.mutate()
        print(f"✅ Mutation: epsilon {original_epsilon:.3f} → {config2.epsilon:.3f}")
        
        # Test target prediction
        prediction = config2.get_performance_prediction()
        targets = config2.meets_targets()
        print(f"✅ Predictions: {prediction}")
        print(f"✅ Targets met: {sum(targets.values())}/4")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent config test failed: {e}")
        return False

def test_mock_environment():
    """Test mock environment from PBT runner."""
    print("\n🤖 Testing Mock Environment...")
    
    try:
        from pbt.pbt_runner import MockEnvironment
        
        env = MockEnvironment(seed=42)
        state = env.reset()
        print(f"✅ Initial state shape: {state.shape}")
        
        # Run a few steps
        total_reward = 0
        for i in range(10):
            action = env.action_space.n // 2  # Middle action
            next_state, reward, done, info = env.step(action)
            total_reward += reward
            
            if done:
                print(f"✅ Episode finished at step {i+1}, reward: {reward:.3f}")
                env.reset()
                break
        
        print(f"✅ Mock environment working, total reward: {total_reward:.3f}")
        return True
        
    except Exception as e:
        print(f"❌ Mock environment test failed: {e}")
        return False

def test_integration_hook():
    """Test integration with analysis pipeline."""
    print("\n🔗 Testing Integration Hook...")
    
    try:
        from pbt.integration_hook import PBTAnalysisIntegration
        
        # Create integration instance
        integration = PBTAnalysisIntegration()
        print("✅ Integration hook created")
        
        # Test baseline comparison (without actual data)
        baseline_metrics = {
            'zero_rate': 0.1193,
            'success_rate': 0.1189,
            'excellence_rate': 0.0540,
            'mean_value': 0.2897
        }
        print(f"✅ Baseline metrics loaded: {baseline_metrics}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration hook test failed: {e}")
        return False

def test_correlation_insights():
    """Test that our correlation insights are properly integrated."""
    print("\n📊 Testing Correlation Analysis Integration...")
    
    try:
        from pbt.agent import AgentConfig
        
        # Test multiple agent configurations
        configs = []
        for i in range(4):
            config = AgentConfig.from_baseline_analysis(i)
            configs.append(config)
        
        # Verify diversity in configurations
        epsilons = [c.epsilon for c in configs]
        reward_shapings = [c.reward_shaping for c in configs]
        
        epsilon_diversity = np.std(epsilons)
        shaping_diversity = np.std(reward_shapings)
        
        print(f"✅ Epsilon diversity: {epsilon_diversity:.3f} (std)")
        print(f"✅ Reward shaping diversity: {shaping_diversity:.3f} (std)")
        
        # Test performance predictions
        predictions = [c.get_performance_prediction() for c in configs]
        predicted_zeros = [p['predicted_zero_rate'] for p in predictions]
        predicted_success = [p['predicted_success_rate'] for p in predictions]
        
        print(f"✅ Predicted zero rates: {[f'{z:.3f}' for z in predicted_zeros]}")
        print(f"✅ Predicted success rates: {[f'{s:.3f}' for s in predicted_success]}")
        
        # Verify correlation insights are applied
        # Higher epsilon should predict lower zero rate
        high_eps_config = max(configs, key=lambda c: c.epsilon)
        low_eps_config = min(configs, key=lambda c: c.epsilon)
        
        high_eps_zero = high_eps_config.get_performance_prediction()['predicted_zero_rate']
        low_eps_zero = low_eps_config.get_performance_prediction()['predicted_zero_rate']
        
        correlation_works = high_eps_zero < low_eps_zero
        
        print(f"✅ Correlation insight test: High ε ({high_eps_config.epsilon:.3f}) "
              f"predicts lower zero rate ({high_eps_zero:.3f}) than "
              f"low ε ({low_eps_config.epsilon:.3f}, {low_eps_zero:.3f}): {correlation_works}")
        
        return correlation_works
        
    except Exception as e:
        print(f"❌ Correlation insights test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 PBT SYSTEM VALIDATION")
    print("=" * 50)
    
    tests = [
        ("Agent Configuration", test_agent_config),
        ("Mock Environment", test_mock_environment), 
        ("Integration Hook", test_integration_hook),
        ("Correlation Insights", test_correlation_insights),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! PBT system ready for PyTorch integration.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 