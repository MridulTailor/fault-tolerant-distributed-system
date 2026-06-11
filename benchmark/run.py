import time
import random
import copy
import sys
import os

# Add parent dir to path so I can import scheduler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scheduler.strategies import RandomStrategy, LeastLoadedStrategy, MostAvailableCapacityStrategy, BestFitStrategy

NUM_NODES = 1000
NUM_SESSIONS = 10000

def generate_nodes():
    nodes = []
    # Using fixed seed for reproducibility across strategies if needed, though I deepcopy
    random.seed(42)
    for i in range(NUM_NODES):
        cap = random.randint(5, 20) # random capacity between 5 and 20. Total capacity ~ 12500
        nodes.append({
            "id": f"node-{i}",
            "capacity": cap,
            "used": 0,
            "healthy": True
        })
    return nodes

def run_benchmark():
    strategies = {
        "Random": RandomStrategy(),
        "Least Loaded": LeastLoadedStrategy(),
        "Most Available Capacity": MostAvailableCapacityStrategy(),
        "Best Fit": BestFitStrategy()
    }
    
    base_nodes = generate_nodes()
    total_capacity = sum(n["capacity"] for n in base_nodes)
    
    print(f"Benchmarking {NUM_NODES} nodes, {NUM_SESSIONS} sessions (Total Cluster Capacity: {total_capacity})")
    print("-" * 65)
    print(f"{'Strategy':<25} {'Utilization':<15} {'Fragmentation':<15} {'Rejected':<10}")
    print("-" * 65)
    
    for name, strategy in strategies.items():
        nodes = copy.deepcopy(base_nodes)
        rejected = 0
        
        start_time = time.time()
        for _ in range(NUM_SESSIONS):
            best_node = strategy.select_node(nodes)
            if best_node:
                best_node["used"] += 1
            else:
                rejected += 1
        latency = time.time() - start_time
        
        active_nodes = [n for n in nodes if n["used"] > 0]
        if active_nodes:
            utilization = sum((n["used"] / n["capacity"]) * 100 for n in active_nodes) / len(active_nodes)
        else:
            utilization = 0.0
        
        # Fragmentation: percentage of nodes that are partially filled
        partially_filled = sum(1 for n in nodes if 0 < n["used"] < n["capacity"])
        fragmentation_pct = (partially_filled / NUM_NODES) * 100
        
        if fragmentation_pct > 70:
            frag_label = "High"
        elif fragmentation_pct > 30:
            frag_label = "Medium"
        else:
            frag_label = "Low"
            
        print(f"{name:<25} {utilization:5.1f}%          {frag_label:<15} {rejected:<10}")

if __name__ == "__main__":
    run_benchmark()
