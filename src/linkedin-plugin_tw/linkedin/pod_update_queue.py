import time
from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Any, List

from pydantic import BaseModel, Field
from pymemri.data.schema import Edge, Item

from .schema import Account, Tweet


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any = field(compare=False)


class PodUpdate(BaseModel):
    class Config:
        copy_on_model_validation = "none"

    create_items: List[Item] = Field(default_factory=list)
    create_edges: List[Edge] = Field(default_factory=list)
    update_items: List[Item] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

    def __add__(self, other):
        return PodUpdate(
            create_items=self.create_items + other.create_items,
            create_edges=self.create_edges + other.create_edges,
            update_items=self.update_items + other.update_items,
        )

    def __lt__(self, other):
        return self.priority < other.priority

    @property
    def priority(self):
        """Updates that create:
        - Tweets have priority 0
        - Account have priority 1
        - Other updates have priority based on the put time to the queue.
        """
        tweet_types = [item for item in self.create_items if isinstance(item, Tweet)]
        account_types = [
            item for item in self.create_items if isinstance(item, Account)
        ]
        if tweet_types:
            return self.created_at / 1000
        elif account_types:
            return self.created_at / 100
        else:
            return self.created_at

    def is_empty(self):
        return (
            len(self.create_items) == 0
            and len(self.create_edges) == 0
            and len(self.update_items) == 0
        )


class PodQueue:
    def __init__(self) -> None:
        self.queue: PriorityQueue[PodUpdate] = PriorityQueue()

    def empty(self):
        return self.queue.empty()

    def get_batched_updates(self, n: int, timeout: float = 0.1) -> PodUpdate:
        # timeout and n should be tuned
        all_pod_updates = PodUpdate()
        for _ in range(n):
            if self.queue.empty():
                break
            pod_update = self.queue.get(timeout=timeout)
            if pod_update is None:
                continue
            all_pod_updates += pod_update
        return all_pod_updates

    def put(
        self,
        *,
        create_items=None,
        update_items=None,
        create_edges=None,
    ):
        pod_update = PodUpdate(
            create_items=create_items or [],
            create_edges=create_edges or [],
            update_items=update_items or [],
        )
        self.queue.put(pod_update)
