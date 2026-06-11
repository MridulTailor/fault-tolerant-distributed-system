import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class SchedulingStrategy(ABC):
    @abstractmethod
    def select_node(self, nodes: List[Dict]) -> Optional[Dict]:
        """
        Selects a node from the given list based on the scheduling strategy.
        Nodes should have 'id', 'capacity', 'used', and 'healthy' keys.
        """
        pass

class RandomStrategy(SchedulingStrategy):
    def select_node(self, nodes: List[Dict]) -> Optional[Dict]:
        available = [n for n in nodes if n.get("healthy", True) and n["used"] < n["capacity"]]
        if not available:
            return None
        return random.choice(available)

class LeastLoadedStrategy(SchedulingStrategy):
    def select_node(self, nodes: List[Dict]) -> Optional[Dict]:
        available = [n for n in nodes if n.get("healthy", True) and n["used"] < n["capacity"]]
        if not available:
            return None
        # Choose node with lowest utilization (used / capacity)
        return min(available, key=lambda n: n["used"] / n["capacity"])

class MostAvailableCapacityStrategy(SchedulingStrategy):
    def select_node(self, nodes: List[Dict]) -> Optional[Dict]:
        available = [n for n in nodes if n.get("healthy", True) and n["used"] < n["capacity"]]
        if not available:
            return None
        # Choose node with most free slots
        return max(available, key=lambda n: n["capacity"] - n["used"])

class BestFitStrategy(SchedulingStrategy):
    def select_node(self, nodes: List[Dict]) -> Optional[Dict]:
        available = [n for n in nodes if n.get("healthy", True) and n["used"] < n["capacity"]]
        if not available:
            return None
        # Choose smallest node (by total capacity) that can still fit the workload (has at least 1 free slot)
        return min(available, key=lambda n: n["capacity"])
