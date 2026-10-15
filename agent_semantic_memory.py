from dataclasses import dataclass
from typing import Dict, List
from collections import Counter
import math
import re
import time


@dataclass
class Memory:
    memory_id: int
    text: str
    vector: Dict[str, float]
    importance: float
    created_at: float
    access_count: int = 0


class SemanticMemory:

    def __init__(self, capacity: int = 100):

        self.capacity = capacity
        self.memories: List[Memory] = []
        self.next_id = 1

    def tokenize(self, text: str) -> List[str]:

        return re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )

    def embed(self, text: str) -> Dict[str, float]:

        tokens = self.tokenize(text)

        if not tokens:
            return {}

        counts = Counter(tokens)
        total = len(tokens)

        return {
            word: count / total
            for word, count in counts.items()
        }

    def cosine_similarity(
        self,
        a: Dict[str, float],
        b: Dict[str, float]
    ) -> float:

        keys = set(a) | set(b)

        dot = sum(
            a.get(k, 0) * b.get(k, 0)
            for k in keys
        )

        magnitude_a = math.sqrt(
            sum(x * x for x in a.values())
        )

        magnitude_b = math.sqrt(
            sum(x * x for x in b.values())
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot / (
            magnitude_a * magnitude_b
        )

    def store(
        self,
        text: str,
        importance: float = 1.0
    ):

        memory = Memory(
            memory_id=self.next_id,
            text=text,
            vector=self.embed(text),
            importance=importance,
            created_at=time.time()
        )

        self.next_id += 1

        self.memories.append(memory)

        self._enforce_capacity()

    def _enforce_capacity(self):

        if len(self.memories) <= self.capacity:
            return

        self.memories.sort(
            key=self._retention_score
        )

        self.memories.pop(0)

    def _retention_score(
        self,
        memory: Memory
