import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from typing import Dict, List, Optional

from loguru import logger
from pymemri.data.schema import Item, PluginRun
from pymemri.pod.client import PodClient

from linkedin.pod_update_queue import PodQueue

from .config import MAX_RESULTS, PAGE_LIMIT


class ItemConsumer:
    def __init__(
        self,
        *,
        client: PodClient,
        queue: PodQueue,
        plugin_run: Optional[PluginRun] = None,
    ) -> None:
        self.queue = queue
        self.client = client
        self.will_stop = False
        self.plugin_run = plugin_run
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.thread = Thread(target=self.consume_thread)

        self.item_counts: Dict[str, int] = defaultdict(int)

    def start(self):
        self.start_time = time.time()
        self.will_stop = False
        self.thread = Thread(target=self.consume_thread)
        self.thread.start()

    def add_count(self, create_items):
        # Count the types in create_items and print
        for item in create_items:
            self.item_counts[item.__class__.__name__] += 1
        logger.info(self.item_counts)

    @property
    def tweets_in_pod(self):
        return self.item_counts["Tweet"]

    @property
    def progress(self):
        return max(0.3, min(1, self.tweets_in_pod / (MAX_RESULTS * PAGE_LIMIT)))

    def update_progress(self, update_items: List[Item]):
        if self.plugin_run is None or self.progress == self.plugin_run.progress:
            return

        if self.plugin_run.progress is None or self.progress > self.plugin_run.progress:
            logger.info(f"Progress update: {self.progress}")
            self.plugin_run.progress = self.progress
            update_items.append(self.plugin_run)

    def consume_thread(self):
        while not (self.will_stop and self.queue.empty()):
            pod_update = self.queue.get_batched_updates(100)
            if pod_update.is_empty():
                continue

            self.update_progress(pod_update.update_items)

            is_ok = self.client.bulk_action(
                create_items=pod_update.create_items,
                create_edges=pod_update.create_edges,
                update_items=pod_update.update_items,
            )
            self.add_count(pod_update.create_items)

            self.executor.submit(self.upload_photo_data, pod_update.create_items)
            if not is_ok:
                logger.error("Error in bulk action")

    def upload_photo_data(self, items: List[Item]):
        photo_items = [item for item in items if item.__class__.__name__ == "Photo"]
        for photo in photo_items:
            is_ok = self.client._upload_image(photo.data, asyncFlag=False)
            if not is_ok:
                logger.error("Error in uploading image")

    def join(self):
        self.will_stop = True
        self.thread.join()
