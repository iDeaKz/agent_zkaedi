#!/usr/bin/env python3
"""
Integration: Hazard-Driven Circuit Breaker with Elite AI Agent System
Shows how to protect agent data loading and API endpoints
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import time

# Assuming hazard_circuit_breaker is imported
from hazard_circuit_breaker import (
    CircuitBreakerManager, RiskStrategy, RiskParams, 
    FeedbackCheckpointer, Mitigation, SecureLogger
)


class ResilientAgentLoader:
    """Agent data loader protected by hazard-driven circuit breaker"""
    
    def __init__(self):
        # Initialize circuit breaker components
        self.logger = SecureLogger(logfile="agent_loader_audit.log")
        self.checkpointer = FeedbackCheckpointer(max_events=1000)
        
        # Configure risk parameters for agent loading
        # Higher theta_fail = more sensitive to failures
        # Higher threshold = more tolerant before opening
        params = RiskParams(
            theta0=-1.0,      # Base risk level
            theta_fail=0.5,   # Failure rate weight
            theta_season=0.3, # Time-of-day weight  
            theta_vol=0.2,    # Volatility weight
            theta_sev=0.8,    # Severity weight
            threshold=1.5     # Risk threshold
        )
        
        self.strategy = RiskStrategy(params)
        self.strategy.set_budgets(
            time_budget=0.5,  # 500ms timeout for loading
            memory_budget=50 * 1024 * 1024  # 50MB limit
        )
        
        # Cache for agent summaries
        self.agent_cache = {}
        
        # Setup mitigation with cache
        self.mitigation = Mitigation(
            fallback={"status": "cached", "records": 0},
            cache=self.agent_cache
        )
        self.strategy.set_mitigation(self.mitigation)
        
        # Create circuit breaker
        self.circuit_breaker = CircuitBreakerManager(
            strategy=self.strategy,
            cp=self.checkpointer,
            mitigation=self.mitigation,
            logger=self.logger,
            cooldown=5.0  # 5 second cooldown
        )
        
    def load_agent_data(self, agent_id: int) -> Dict[str, Any]:
        """Load agent data with circuit breaker protection"""
        
        def _load():
            filepath = Path(f"data/agent_{agent_id}/agent_{agent_id}_full_dump.json")
            
            if not filepath.exists():
                raise FileNotFoundError(f"Agent {agent_id} data not found")
                
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Create summary for caching
            summary = {
                "agent_id": agent_id,
                "records": len(data),
                "status": "loaded",
                "sample": data[:10] if data else []  # Cache first 10 records
            }
            
            # Cache the summary
            self.agent_cache[agent_id] = summary
            
            return summary
            
        # Execute with circuit breaker protection
        return self.circuit_breaker.execute(_load, key=agent_id)
        
    def load_all_agents(self, agent_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Load multiple agents with circuit breaker protection"""
        results = {}
        
        for agent_id in agent_ids:
            try:
                result = self.load_agent_data(agent_id)
                results[agent_id] = result
                print(f"✅ Agent {agent_id}: {result['status']} ({result['records']} records)")
            except Exception as e:
                print(f"❌ Agent {agent_id}: Failed - {e}")
                results[agent_id] = {"status": "error", "error": str(e)}
                
        return results


class ResilientAPIEndpoint:
    """API endpoint protection with circuit breaker"""
    
    def __init__(self):
        # Separate circuit breaker for API calls
        self.logger = SecureLogger(logfile="api_audit.log")
        self.checkpointer = FeedbackCheckpointer(max_events=500)
        
        # More aggressive parameters for API protection
        params = RiskParams(
            theta0=-0.5,
            theta_fail=1.0,   # Very sensitive to failures
            theta_season=0.5,
            theta_vol=0.5,
            theta_sev=1.0,
            threshold=1.0     # Lower threshold
        )
        
        self.strategy = RiskStrategy(params)
        self.strategy.set_budgets(
            time_budget=0.1,  # 100ms timeout for API calls
            memory_budget=10 * 1024 * 1024  # 10MB limit
        )
        
        # API response cache
        self.response_cache = {}
        self.mitigation = Mitigation(
            fallback={"status": "service_unavailable", "cached": True},
            cache=self.response_cache
        )
        self.strategy.set_mitigation(self.mitigation)
        
        self.circuit_breaker = CircuitBreakerManager(
            strategy=self.strategy,
            cp=self.checkpointer,
            mitigation=self.mitigation,
            logger=self.logger,
            cooldown=3.0
        )
        
    def call_endpoint(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make API call with circuit breaker protection"""
        
        cache_key = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        
        def _call():
            # Simulate API call
            import requests
            
            response = requests.get(
                f"http://localhost:8000{endpoint}",
                params=params,
                timeout=0.1
            )
            
            result = {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None,
                "cached": False
            }
            
            # Cache successful responses
            if response.status_code == 200:
                self.response_cache[cache_key] = result
                
            return result
            
        return self.circuit_breaker.execute(_call, key=cache_key)


def demonstrate_integration():
    """Show how circuit breaker helps with our bottlenecks"""
    print("🚀 CIRCUIT BREAKER INTEGRATION DEMO")
    print("="*60)
    
    # Test agent loader
    print("\n1️⃣ AGENT DATA LOADING WITH PROTECTION:")
    loader = ResilientAgentLoader()
    
    # Load agents 0-4
    results = loader.load_all_agents([0, 1, 2, 3, 4])
    
    # Show circuit breaker stats
    risk = loader.strategy.evaluate_risk(loader.checkpointer)
    print(f"\n📊 Current risk level: {risk:.3f}")
    print(f"   Circuit state: {loader.circuit_breaker.state}")
    
    # Test API protection
    print("\n2️⃣ API ENDPOINT PROTECTION:")
    api = ResilientAPIEndpoint()
    
    endpoints = ["/health", "/api/agents", "/api/metrics"]
    
    for endpoint in endpoints:
        try:
            result = api.call_endpoint(endpoint)
            status = "cached" if result.get("cached") else "live"
            print(f"✅ {endpoint}: {status} response")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
            
    print("\n💡 BENEFITS DEMONSTRATED:")
    print("   ✅ Timeout protection (500ms for agents, 100ms for API)")
    print("   ✅ Automatic caching of successful responses")
    print("   ✅ Graceful degradation with fallbacks")
    print("   ✅ Risk-based circuit opening")
    print("   ✅ Tamper-evident audit trail")


if __name__ == "__main__":
    demonstrate_integration() 