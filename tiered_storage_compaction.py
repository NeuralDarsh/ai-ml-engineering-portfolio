# Cloud Storage & Data Warehousing: Consolidating fragmented hot-tier blocks and migrating cold data across storage tiers

import time
import json
import uuid

class StorageBlock:
    """Represents an immutable data block residing in a storage tier."""
    def __init__(self, records, tier="HOT"):
        self.block_id = f"blk_{uuid.uuid4().hex[:8]}"
        self.records = records
        self.record_count = len(records)
        self.tier = tier
        self.created_at = time.time()


class TieredStorageLifecycleEngine:
    """
    Manages data block lifecycle across HOT, WARM, and COLD tiers.
    Compacts small fragmented blocks in the HOT tier and transitions aged blocks to cheaper tiers.
    """
    def __init__(self, hot_compaction_threshold=3, warm_age_seconds=1.5, cold_age_seconds=3.0):
        self.hot_compaction_threshold = hot_compaction_threshold
        self.warm_age_seconds = warm_age_seconds
        self.cold_age_seconds = cold_age_seconds
        self.tiers = {
            "HOT": [],
            "WARM": [],
            "COLD": []
        }

    def ingest_hot_block(self, records):
        """Ingests new uncompacted data directly into the low-latency HOT tier."""
        block = StorageBlock(records, tier="HOT")
        self.tiers["HOT"].append(block)
        print(f" [INGEST HOT] Block '{block.block_id}' stored ({block.record_count} records).")
        return block

    def run_hot_compaction(self):
        """Merges multiple small HOT tier blocks into a single consolidated block."""
        print("\n--- Storage Lifecycle: Running HOT Tier Compaction ---")
        hot_blocks = self.tiers["HOT"]

        if len(hot_blocks) < self.hot_compaction_threshold:
            print(f" Compaction threshold not met ({len(hot_blocks)}/{self.hot_compaction_threshold} blocks). Skipping.")
            return None

        merged_records = []
        compacted_block_ids = []

        for blk in hot_blocks:
            merged_records.extend(blk.records)
            compacted_block_ids.append(blk.block_id)

        # Deduplicate and sort records
        merged_records = sorted(list(set(merged_records)))
        compacted_block = StorageBlock(merged_records, tier="HOT")

        # Replace fragmented blocks with single consolidated block
        self.tiers["HOT"] = [compacted_block]

        print(f" [COMPACTED] Merged {len(compacted_block_ids)} blocks into '{compacted_block.block_id}'.")
        print(f"  -> Source Blocks: {compacted_block_ids}")
        print(f" -> Compacted Record Count: {compacted_block.record_count}\n")
        return compacted_block

    def run_lifecycle_migration(self):
        """Evaluates block ages and transitions them from HOT -> WARM -> COLD."""
        print("--- Storage Lifecycle: Evaluating Tier Migrations ---")
        now = time.time()

        # Check HOT -> WARM transition
        remaining_hot = []
        for blk in self.tiers["HOT"]:
            if (now - blk.created_at) >= self.warm_age_seconds:
                blk.tier = "WARM"
                self.tiers["WARM"].append(blk)
                print(f" [TIER SHIFT: HOT -> WARM] Block '{blk.block_id}' moved to object storage.")
            else:
                remaining_hot.append(blk)
        self.tiers["HOT"] = remaining_hot

        # Check WARM -> COLD transition
        remaining_warm = []
        for blk in self.tiers["WARM"]:
            if (now - blk.created_at) >= self.cold_age_seconds:
                blk.tier = "COLD"
                self.tiers["COLD"].append(blk)
                print(f" [TIER SHIFT: WARM -> COLD] Block '{blk.block_id}' archived to cold storage.")
            else:
                remaining_warm.append(blk)
        self.tiers["WARM"] = remaining_warm

    def get_tier_summary(self):
        return {
            tier: [b.block_id for b in blocks]
            for tier, blocks in self.tiers.items()
        }


if __name__ == "__main__":
    print("--- Cloud Storage: Tiered Storage & Compaction Simulator ---\n")

    engine = TieredStorageLifecycleEngine(
        hot_compaction_threshold=3,
        warm_age_seconds=1.0,
        cold_age_seconds=2.0
    )

    # 1. Ingest small burst of fragmented blocks
    print("Step 1: Ingesting fragmented data into HOT tier:")
    engine.ingest_hot_block(["event_1", "event_2"])
    engine.ingest_hot_block(["event_3"])
    engine.ingest_hot_block(["event_4", "event_5"])

    # 2. Run compaction pass
    engine.run_hot_compaction()

    # 3. Simulate passage of time for tier aging
    print("Sleeping 1.2s for WARM tier aging...\n")
    time.sleep(1.2)
    engine.run_lifecycle_migration()

    print("\nSleeping 1.1s for COLD tier archive aging...\n")
    time.sleep(1.1)
    engine.run_lifecycle_migration()

    # 4. Final summary
    print("\nFinal Tier Distribution:")
    print(json.dumps(engine.get_tier_summary(), indent=2))