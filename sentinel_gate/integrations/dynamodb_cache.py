import hashlib
import time
from typing import Optional, Dict, Any
import boto3
from sentinel_gate.config import settings

class DynamoDBCacheService:
    """
    Amazon DynamoDB Decision Cache.
    Caches SHA-256 prompt hashes and classification decisions for sub-millisecond replay lookups.
    """

    def __init__(self):
        self.table_name = settings.DYNAMODB_TABLE_NAME
        self.region = settings.AWS_REGION
        self._dynamodb = None
        self._table = None
        self._local_cache: Dict[str, Dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0
        self._init_client()

    def _init_client(self):
        try:
            self._dynamodb = boto3.resource("dynamodb", region_name=self.region)
            self._table = self._dynamodb.Table(self.table_name)
        except Exception:
            self._table = None

    @staticmethod
    def hash_prompt(prompt: str) -> str:
        return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()

    def get(self, prompt: str) -> Optional[Dict[str, Any]]:
        prompt_hash = self.hash_prompt(prompt)

        # 1. Fast local cache check (<0.1ms)
        if prompt_hash in self._local_cache:
            entry = self._local_cache[prompt_hash]
            if time.time() - entry.get("timestamp", 0) < 3600:  # 1 hour TTL
                self.hits += 1
                return entry["data"]

        # 2. DynamoDB lookup if configured
        if self._table:
            try:
                res = self._table.get_item(Key={"prompt_hash": prompt_hash})
                if "Item" in res:
                    self.hits += 1
                    data = res["Item"]["decision_data"]
                    self._local_cache[prompt_hash] = {"data": data, "timestamp": time.time()}
                    return data
            except Exception:
                pass

        self.misses += 1
        return None

    def put(self, prompt: str, decision_data: Dict[str, Any]):
        prompt_hash = self.hash_prompt(prompt)
        entry = {
            "prompt_hash": prompt_hash,
            "decision_data": decision_data,
            "timestamp": int(time.time()),
            "ttl": int(time.time() + 86400)  # 24 hour DynamoDB TTL
        }

        # Store in local LRU/dict
        self._local_cache[prompt_hash] = {"data": decision_data, "timestamp": time.time()}

        # Store in DynamoDB table if available
        if self._table:
            try:
                self._table.put_item(Item=entry)
            except Exception:
                pass

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return round((self.hits / total) * 100.0, 2) if total > 0 else 0.0

dynamodb_cache = DynamoDBCacheService()
