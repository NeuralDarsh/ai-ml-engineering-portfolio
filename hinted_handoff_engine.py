# Distributed Storage & High Availability: Buffering writes for unavailable replicas and replaying on node recovery

import time
import json

class TargetNode:
    """Represents an independent replica storage node."""
    def __init__(self, node_id, is_online=True):
        self.node_id = node_id
        self.is_online = is_online
        self.storage = {}

    def write(self, key, value):
        if not self.is_online:
            raise ConnectionError(f"Node '{self.node_id}' is unreachable.")
        self.storage[key] = value
        return True


class HintedHandoffCoordinator:
    """
    Coordinates writes across replica nodes.
    Buffers unacknowledged mutations as hints when replicas are offline,
    replaying them when nodes recover.
    """
    def __init__(self, hint_ttl=10.0):
        self.hint_ttl = hint_ttl
        # target_node_id -> list of hint dicts
        self.hint_buffer = {}

    def execute_write(self, node, key, value):
        """Attempts direct write; on connection failure, stores a hinted handoff record."""
        print(f"--- Inbound Write: Key='{key}' -> Target Node='{node.node_id}' ---")
        try:
            node.write(key, value)
            print(f"  DIRECT WRITE SUCCESS: Node '{node.node_id}' committed '{key}' = '{value}'.\n")
            return True
        except ConnectionError as err:
            print(f"DIRECT WRITE FAILED: {err}")
            self._buffer_hint(node.node_id, key, value)
            return False

    def _buffer_hint(self, target_node_id, key, value):
        """Stores a mutation hint with a timestamp for later asynchronous replay."""
        if target_node_id not in self.hint_buffer:
            self.hint_buffer[target_node_id] = []

        hint_entry = {
            "key": key,
            "value": value,
            "buffered_at": time.time(),
            "target_node_id": target_node_id
        }
        self.hint_buffer[target_node_id].append(hint_entry)
        print(f" [HINT BUFFERED] Preserved mutation for '{target_node_id}' in coordinator queue.\n")

    def replay_hints_for_node(self, node):
        """Replays buffered hints to a restored replica and purges expired entries."""
        print(f"[REPLAY ROUTINE] Checking buffered hints for '{node.node_id}'...")
        hints = self.hint_buffer.get(node.node_id, [])

        if not hints:
            print(f" No buffered hints found for '{node.node_id}'.\n")
            return 0

        now = time.time()
        active_hints = []
        replayed_count = 0

        for hint in hints:
            # Drop hints exceeding configured TTL
            if now - hint["buffered_at"] > self.hint_ttl:
                print(f" [HINT EXPIRED] Dropping stale hint for key '{hint['key']}'.")
                continue

            try:
                node.write(hint["key"], hint["value"])
                replayed_count += 1
                print(f" [HINT REPLAYED] Flushed '{hint['key']}' = '{hint['value']}' to '{node.node_id}'.")
            except ConnectionError:
                # If still failing, retain for next cycle
                active_hints.append(hint)

        self.hint_buffer[node.node_id] = active_hints
        print(f"Replay completed: {replayed_count} mutations flushed to '{node.node_id}'.\n")
        return replayed_count


if __name__ == "__main__":
    print("--- Distributed Storage: Hinted Handoff Replay Engine ---\n")

    coordinator = HintedHandoffCoordinator(hint_ttl=5.0)
    replica_node = TargetNode("node_tokyo_replica_1", is_online=True)

    # 1. Successful write while node is healthy
    coordinator.execute_write(replica_node, "config:max_workers", 16)

    # 2. Simulate replica failure / network blip
    print("Simulating node degradation: 'node_tokyo_replica_1' goes offline.\n")
    replica_node.is_online = False

    # 3. Writes arrive during downtime (buffered as hints)
    coordinator.execute_write(replica_node, "config:max_workers", 32)
    coordinator.execute_write(replica_node, "feature:experimental_ai", "enabled")

    # 4. Replica recovers and comes back online
    print("'node_tokyo_replica_1' recovered and back online.")
    replica_node.is_online = True

    # 5. Coordinator replays buffered hints to restore consistency
    coordinator.replay_hints_for_node(replica_node)

    # 6. Verify restored replica state
    print("Final Storage State on 'node_tokyo_replica_1':")
    print(json.dumps(replica_node.storage, indent=2))