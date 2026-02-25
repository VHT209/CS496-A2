import requests
import logging
import concurrent
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import REQUEST_TIMEOUT_SECONDS, HTTP_OK, COORDINATOR_INITIAL_VOTE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def write_message_quorum(message, peers):
    """
    Writes a message to the cluster using a Quorum consensus.
    
    Args:
        message (dict): The message payload.
        peers (list): List of peer URLs.
        
    Returns:
        bool: True if Quorum achieved, False otherwise.
    """
    count = COORDINATOR_INITIAL_VOTE  # Start with coordinator's vote
    with concurrent.futures.ThreadPoolExecutor(len(peers)) as executor:
        # Send POST requests to all peers in parallel
        future_results = {executor.submit(requests.post, peer + "/internal/write", json=message, timeout = REQUEST_TIMEOUT_SECONDS): peer for peer in peers}
        for future_response in concurrent.futures.as_completed(future_results):
            # Check the result of each request and increment count depending on the number of 200 responses
            peer_responded_url = future_results[future_response]
            try:
                response = future_response.result()
                if response.status_code == HTTP_OK:
                    count += 1
                    logger.info(f"Peer {peer_responded_url} voted YES for message {message['id']}")
                else:
                    logger.warning(f"Peer {peer_responded_url} voted NO for message {message['id']} with status code {response.status_code}")
            except Exception as e:
                logger.warning(f"Error processing response from peer {peer_responded_url}: {e}")
    # Check if the count is greater than half of the total # of peers + the coordinator
    if count > (len(peers) + COORDINATOR_INITIAL_VOTE) / 2:         #(len(peers) + 1) = total number of nodes including coordinator
        return True, count 
    return False, count
    

