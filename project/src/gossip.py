import time
import threading
import random
import requests
import logging
from constants import (
    GOSSIP_INTERVAL_MIN_SECONDS, GOSSIP_INTERVAL_MAX_SECONDS,
    REQUEST_TIMEOUT_SECONDS, HTTP_OK
)

logger = logging.getLogger(__name__)

class GossipProtocol:
    def __init__(self, node_id, peers, storage):
        self.node_id = node_id
        self.peers = peers
        self.storage = storage
        self.running = True

    def start(self):
        """Starts the background gossip thread."""
        thread = threading.Thread(target=self.gossip_loop, daemon=True)
        thread.start()

    def gossip_loop(self):
        logger.info("Gossip protocol started.")
        while self.running:
            try:
              self.sync_with_peer(random.choice(self.peers))
            except Exception as e:
              logger.warning(f"Error during gossip sync: {e}")
            #Sleep for a random interval between MIN & MAX
            sleep_time = random.uniform(GOSSIP_INTERVAL_MIN_SECONDS, GOSSIP_INTERVAL_MAX_SECONDS)
            logger.debug(f"Sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)

    def sync_with_peer(self, peer_url):
        data_from_peer = requests.get(url=peer_url + "/messages", timeout=REQUEST_TIMEOUT_SECONDS)
        if data_from_peer.status_code == HTTP_OK:
            # return empty list as default if key is missing
            peer_messages = data_from_peer.json().get("messages", [])
            # Compare peer messages with local storage and add any new messages to local storage for those with unique ids
            new_messages = [msg for msg in peer_messages if not any(current_message["id"] == msg["id"] for current_message in self.storage)]
            if new_messages:
                logger.info(f"Received {len(new_messages)} new messages from peer {peer_url}.")
                self.storage.extend(new_messages)
            else:
                logger.debug(f"No new messages received from peer {peer_url}.")
        else:
            logger.warning(f"Failed to sync with peer {peer_url}. Status code: {data_from_peer.status_code}")
            
def start_gossip_thread(node_id, peers, storage):
    gossip = GossipProtocol(node_id, peers, storage)
    gossip.start()
    return gossip
