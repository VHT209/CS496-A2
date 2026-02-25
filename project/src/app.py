from flask import Flask, request, jsonify
import os
import uuid
import threading
import logging
from node_manager import get_peers, get_node_id
from constants import (
    MODE_STRONG, MODE_EVENTUAL, DEFAULT_USER, DEFAULT_TIMESTAMP,
    DEFAULT_PORT, HTTP_OK, HTTP_ACCEPTED, HTTP_BAD_REQUEST, HTTP_INTERNAL_SERVER_ERROR
)
import quorum
import gossip

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage
MESSAGES = []

# Configuration
MODE = os.environ.get("MODE", MODE_STRONG)  # STRONG or EVENTUAL
NODE_ID = get_node_id()
PEERS = get_peers()

if MODE == MODE_EVENTUAL:
    gossip.start_gossip_thread(NODE_ID, PEERS, MESSAGES) 

@app.route('/')
def health():
    return jsonify({"status": "up", "node_id": NODE_ID, "mode": MODE})

@app.route('/messages', methods=['GET'])
def get_messages():
    """Retrieve all messages."""
    return jsonify({"messages": MESSAGES, "count": len(MESSAGES)})

@app.route('/message', methods=['POST'])
def post_message():
    """
    Public endpoint for clients to post messages.
    Handles consistency logic based on MODE.
    """
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid payload"}), HTTP_BAD_REQUEST

    # Enrich message with metadata
    message = {
        "id": str(uuid.uuid4()),
        "text": data['text'],
        "user": data.get("user", DEFAULT_USER),
        "timestamp": data.get("timestamp", DEFAULT_TIMESTAMP),
        "origin_node": NODE_ID
    }

    if MODE == MODE_STRONG:
        try:
            # Add MESSAGES to commit locally easier
            success, count = quorum.write_message_quorum(message, PEERS)
            if success:
                # Check in case of locally committing twice
                if not any(previousMessages['id'] == message['id'] for previousMessages in MESSAGES):
                    MESSAGES.append(message)
                return jsonify({"status": "committed", 
                                "mode":   "quorum",
                                "replicas": count,
                                "message_id": message['id']}), HTTP_OK
            else:
                return jsonify({"error": "quorum failed to reach"}), HTTP_INTERNAL_SERVER_ERROR
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "quorum mode unknown error"}), HTTP_INTERNAL_SERVER_ERROR

    elif MODE == MODE_EVENTUAL:
        try:
            MESSAGES.append(message)
            return jsonify({"status": "accepted", 
                                "mode":   "gossip",
                                "note": "Propagation in progress",
                                "message_id": message['id']}), HTTP_ACCEPTED
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "gossip mode unknown error"}), HTTP_INTERNAL_SERVER_ERROR
    else:
        return jsonify({"error": "Unknown mode"})



@app.route('/internal/write', methods=['POST'])
def internal_write():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid payload"}), HTTP_BAD_REQUEST
    # Check duplicate message ID 
    elif any(previousMessages['id'] == data['id'] for previousMessages in MESSAGES):
        return jsonify({"error": "Duplicate message ID"}), HTTP_BAD_REQUEST
    else:
        MESSAGES.append(data)
        return jsonify({"message": "committed"}), HTTP_OK

if __name__ == '__main__':
    port = int(os.environ.get('PORT', DEFAULT_PORT))
    app.run(host='0.0.0.0', port=port, threaded=True)
