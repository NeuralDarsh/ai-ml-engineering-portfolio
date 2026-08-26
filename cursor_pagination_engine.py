# Database & API Architecture: Implementing keyset cursor pagination with Base64 opaque token encoding

import base64
import json

class CursorPaginationEngine:
    """
    Implements cursor-based (keyset) pagination for high-throughput APIs.
    Encodes sorting keys into opaque Base64 tokens to ensure O(1) page lookups.
    """
    def __init__(self, primary_key="id"):
        self.primary_key = primary_key

    def encode_cursor(self, record):
        """Encodes the sort key from a record into an opaque Base64 token."""
        cursor_data = {"last_id": record[self.primary_key]}
        serialized = json.dumps(cursor_data).encode("utf-8")
        return base64.urlsafe_b64encode(serialized).decode("utf-8")

    def decode_cursor(self, cursor_token):
        """Decodes an opaque Base64 cursor back into target record metadata."""
        if not cursor_token:
            return None
        try:
            decoded_bytes = base64.urlsafe_b64decode(cursor_token.encode("utf-8"))
            return json.loads(decoded_bytes.decode("utf-8"))
        except Exception:
            raise ValueError("Malformed or invalid pagination cursor token.")

    def paginate_dataset(self, dataset, limit=3, cursor=None):
        """
        Extracts a page slice from an ordered dataset using cursor boundary logic.
        """
        print("--- Database Architecture: Keyset Cursor Pagination ---")
        print(f"Limit: {limit} | Ingested Cursor: {cursor}")

        start_index = 0
        if cursor:
            cursor_info = self.decode_cursor(cursor)
            target_id = cursor_info.get("last_id")
            for idx, item in enumerate(dataset):
                if item[self.primary_key] == target_id:
                    start_index = idx + 1
                    break

        page_items = dataset[start_index : start_index + limit]
        has_next_page = (start_index + limit) < len(dataset)

        next_cursor = self.encode_cursor(page_items[-1]) if (has_next_page and page_items) else None

        result = {
            "data": page_items,
            "pagination": {
                "limit": limit,
                "has_next_page": has_next_page,
                "next_cursor": next_cursor
            }
        }

        print(f"Fetched Records: {len(page_items)}")
        print(f"Has Next Page  : {has_next_page}")
        print(f"Next Cursor    : {next_cursor}\n")
        return result

if __name__ == "__main__":
    # Simulated sorted database collection
    mock_db_records = [
        {"id": 101, "title": "System Design Overview", "views": 1500},
        {"id": 102, "title": "Database Sharding", "views": 2400},
        {"id": 103, "title": "In-Memory Caching", "views": 3100},
        {"id": 104, "title": "Message Queues (Kafka)", "views": 4200},
        {"id": 105, "title": "Circuit Breakers in Prod", "views": 5300},
        {"id": 106, "title": "GraphQL vs REST", "views": 6100},
        {"id": 107, "title": "Docker Orchestration", "views": 7800}
    ]

    engine = CursorPaginationEngine(primary_key="id")

    # 1. Fetch Page 1 (No cursor provided)
    print("Fetching Page 1:")
    page_1 = engine.paginate_dataset(mock_db_records, limit=3)

    # 2. Fetch Page 2 using cursor from Page 1
    cursor_page_2 = page_1["pagination"]["next_cursor"]
    print("Fetching Page 2 (Using Cursor):")
    page_2 = engine.paginate_dataset(mock_db_records, limit=3, cursor=cursor_page_2)