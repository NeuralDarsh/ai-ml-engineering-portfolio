# Distributed Systems & Storage: Implementing Dynamo-style quorum consensus (R + W > N) with versioned read-repair

import time

class StorageNode:
    """Represents an independent storage replica node holding versioned data."""
    def __init__(self, node_id, is_online=True):
        self.node_id = node_id
        self.is_online = is_online
        self.store = {}  # key -> {"val": data, "version": int, "timestamp": float}

    def write(self, key, value, version):
        if not self.is_online:
            return False
        self.store[key] = {
            "val": value,
            "version": version,
            "timestamp": time.time()
        }
        return True

    def read(self, key):
        if not self.is_online:
            return None
        return self.store.get(key)


class QuorumConsensusEngine:
    """
    Coordinates distributed read and write quorums across N storage replicas.
    Enforces R + W > N consistency guarantees and triggers read-repairs on stale nodes.
    """
    def __init__(self, nodes, write_quorum=2, read_quorum=2):
        self.nodes = nodes
        self.n = len(nodes)
        self.w = write_quorum
        self.r = read_quorum
        self.key_versions = {}

    def write(self, key, value):
        print(f"--- Quorum Write: Key='{key}', Val='{value}' (W={self.w}/{self.n}) ---")
        version = self.key_versions.get(key, 0) + 1
        successful_writes = 0

        for node in self.nodes:
            if node.write(key, value, version):
                successful_writes += 1
                print(f" [ACK WRITE] Node '{node.node_id}' committed v{version}.")
            else:
                print(f" [FAIL WRITE] Node '{node.node_id}' unreachable.")

        if successful_writes >= self.w:
            self.key_versions[key] = version
            print(f" WRITE QUORUM ACHIEVED: {successful_writes}/{self.n} ACKs confirmed.\n")
            return True
        else:
            print(f" WRITE QUORUM FAILED: Only {successful_writes}/{self.w} required ACKs received.\n")
            return False

    def read(self, key):
        print(f"--- Quorum Read: Key='{key}' (R={self.r}/{self.n}) ---")
        responses = []

        for node in self.nodes:
            record = node.read(key)
            if record:
                responses.append((node, record))
                print(f" [ACK READ] Node '{node.node_id}' returned v{record['version']}: '{record['val']}'")
            else:
                print(f" [MISS/OFFLINE] Node '{node.node_id}' returned no data.")

        if len(responses) < self.r:
            print(f" READ QUORUM FAILED: Insufficient read replicas ({len(responses)}/{self.r}).\n")
            return None

        # Resolve the latest record by version
        latest_node, latest_record = max(responses, key=lambda item: item[1]["version"])
        print(f"CONSENSUS REACHED: Latest value is '{latest_record['val']}' (v{latest_record['version']})")

        # Read-Repair: Detect stale nodes and silently update them
        for node, record in responses:
            if record["version"] < latest_record["version"]:
                print(f" [READ-REPAIR] Syncing stale node '{node.node_id}' to v{latest_record['version']}...")
                node.write(key, latest_record["val"], latest_record["version"])

        print(f"READ COMPLETE\n")
        return latest_record["val"]


if __name__ == "__main__":
    # Cluster setup: N = 3 replicas, W = 2, R = 2 (R + W = 4 > 3 -> Strong Consistency)
    node_a = StorageNode("replica_us_1")
    node_b = StorageNode("replica_us_2")
    node_c = StorageNode("replica_eu_1")

    cluster = QuorumConsensusEngine([node_a, node_b, node_c], write_quorum=2, read_quorum=2)

    # 1. Initial write with all nodes active
    cluster.write("feature_toggle", "enabled")

    # 2. Simulate node_c going offline during an update
    node_c.is_online = False
    print("Simulating network partition: 'replica_eu_1' goes offline.\n")
    cluster.write("feature_toggle", "disabled_for_maintenance")

    # 3. Node_c comes back online with stale data
    node_c.is_online = True
    print("'replica_eu_1' is back online (holding stale v1 data).\n")

    # 4. Quorum read resolves conflict and triggers automatic read-repair on node_c
    resolved_val = cluster.read("feature_toggle")