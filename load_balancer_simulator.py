# Cloud Infrastructure & Distributed Systems: Simulating Weighted Round-Robin and Least-Connections routing algorithms

import itertools

class LoadBalancerSimulator:
    """
    Simulates application load balancing across backend server pools
    using Weighted Round-Robin and Dynamic Least-Connections strategies.
    """
    def __init__(self, server_nodes):
        # server_nodes: list of dicts -> [{"id": "srv_1", "weight": 3, "active_conns": 2, "is_healthy": True}]
        self.servers = server_nodes
        self._round_robin_cycle = None
        self._build_weighted_cycle()

    def _build_weighted_cycle(self):
        """Generates an interleaved cycle sequence honoring server weights for healthy nodes."""
        pool = []
        for s in self.servers:
            if s.get("is_healthy", True):
                pool.extend([s["id"]] * s.get("weight", 1))
        self._round_robin_cycle = itertools.cycle(pool) if pool else None

    def route_weighted_round_robin(self):
        """Dispatches request via deterministic weighted round-robin distribution."""
        if not self._round_robin_cycle:
            print(" ERROR: No healthy backend servers available in pool.")
            return None
        target_id = next(self._round_robin_cycle)
        print(f" [WEIGHTED-RR] Routed request -> Server '{target_id}'")
        return target_id

    def route_least_connections(self):
        """Dispatches request dynamically to the healthy server with minimum active connections."""
        healthy_nodes = [s for s in self.servers if s.get("is_healthy", True)]
        if not healthy_nodes:
            print(" ERROR: No healthy backend servers available in pool.")
            return None

        # Select node with minimum active connections
        target_node = min(healthy_nodes, key=lambda s: s["active_conns"])
        target_node["active_conns"] += 1  # Simulate connection assignment
        print(f"  [LEAST-CONNS] Routed request -> Server '{target_node['id']}' (Active Conns: {target_node['active_conns']})")
        return target_node["id"]

if __name__ == "__main__":
    print("--- Cloud Infrastructure: Load Balancer Simulator ---\n")

    server_cluster = [
        {"id": "srv_us_east_1", "weight": 3, "active_conns": 5, "is_healthy": True},
        {"id": "srv_us_east_2", "weight": 2, "active_conns": 1, "is_healthy": True},
        {"id": "srv_eu_west_1", "weight": 1, "active_conns": 0, "is_healthy": True},
        {"id": "srv_ap_northeast_1", "weight": 2, "active_conns": 8, "is_healthy": False}  # Degraded node
    ]

    balancer = LoadBalancerSimulator(server_cluster)

    # 1. Test Weighted Round-Robin Strategy (6 requests)
    print("Test 1: Simulating Weighted Round-Robin Traffic (6 requests):")
    for _ in range(6):
        balancer.route_weighted_round_robin()

    print("\n" + "=" * 55 + "\n")

    # 2. Test Least Connections Strategy (3 requests)
    print("Test 2: Simulating Least Connections Routing (3 requests):")
    for _ in range(3):
        balancer.route_least_connections()