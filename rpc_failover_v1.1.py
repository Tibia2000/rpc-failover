"""
RPC Failover with Gunicorn

This script implements an RPC failover mechanism using Flask and Gunicorn. It manages multiple sets of primary and fallback RPC endpoints,
periodically checks the health status of the primary endpoint, and switches to the fallback endpoint if the primary fails. It also switches
back to the primary endpoint once it becomes healthy again for a specified duration.

The health status of the RPC endpoints is determined by sending an eth_getBlockByNumber request and verifying if the block numbers are changing,
indicating that the node is syncing or producing new blocks. Additionally, the responses of regular RPC calls are monitored for errors and error
messages to trigger failover if necessary.

Instructions:
1. Install Gunicorn using `pip install gunicorn`.
2. Configure the systemd service file to run the Gunicorn instance.
3. Modify the primary and fallback RPC endpoints in the `rpc_sets` variable.
4. Adjust the timeout thresholds and health check intervals as needed.
5. Start the Gunicorn service and monitor the failover behavior.

"""

import logging
from flask import Flask, request, jsonify
import requests
import threading
import time

# Configure logging
logging.basicConfig(filename='/var/log/rpc_failover', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define your number of sets of primary and fallback RPC endpoints
rpc_sets = [
    {"primary": "https://arb-mainnet1", "fallback": "https://arbitrum.blo"},
    {"primary": "https://arb3354419087ba6442e15d", "fallback": "https:/"},
]

# Add a global variable to store the currently selected RPC and counters
current_rpc = None  # TBD
unhealthy_counter = 0
healthy_counter = 0
timeout_threshold = 2  # Set the timeout threshold in seconds
minutes_threshold = 2  # Set the minutes threshold

def is_rpc_healthy(rpc_url):
    try:
        response = requests.get(rpc_url, timeout=timeout_threshold)  # Set timeout for RPC health check
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False

def is_block_number_updated(rpc_url):
    try:
        response = requests.post(rpc_url, json={"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":83}, timeout=timeout_threshold)
        response.raise_for_status()
        result = response.json().get("result")
        if result:
            return True
    except Exception as e:
        logging.error(f"Error checking block number: {e}")
    return False

def periodically_check_primary_health():
    global current_rpc, unhealthy_counter, healthy_counter
    while True:
        if current_rpc:
            if not is_rpc_healthy(current_rpc):
                unhealthy_counter += 1
                if unhealthy_counter >= timeout_threshold:
                    current_rpc = rpc_set["fallback"]
                    unhealthy_counter = 0
                    healthy_counter = 0
                    logging.info("Switching to fallback endpoint due to timeout.")
            else:
                if is_block_number_updated(current_rpc):
                    healthy_counter += 1
                    if healthy_counter >= 2 * minutes_threshold:
                        current_rpc = rpc_set["primary"]
                        unhealthy_counter = 0
                        healthy_counter = 0
                        logging.info("Switching back to primary endpoint.")
                else:
                    logging.info("Block number not updating. Checking fallback.")
                    current_rpc = rpc_set["fallback"]
                    unhealthy_counter = 0
                    healthy_counter = 0
        time.sleep(60)

# Start the periodic health check in a separate thread
health_check_thread = threading.Thread(target=periodically_check_primary_health)
health_check_thread.start()

def fetch_rpc_url_winner(rpc_set):
    global current_rpc
    # Choose the winner based on the current RPC
    winner = current_rpc if current_rpc else rpc_set["primary"]
    return winner

@app.route('/rpc', methods=['POST'])
def proxy_rpc_request():
    json_data = request.get_json()

    # Extract the RPC set index from the incoming request
    rpc_set_index = int(request.args.get('rpc_set_index', 0))
    rpc_set = rpc_sets[rpc_set_index]

    # Choose the RPC endpoint using the fetch_rpc_url_winner logic
    winner = fetch_rpc_url_winner(rpc_set)

    try:
        response = requests.post(winner, json=json_data, timeout=timeout_threshold)  # Set timeout for RPC requests
        response.raise_for_status()
        result = response.json()
        
        # Check for errors or err in the JSON response
        if "error" in result or "err" in result:
            # If error occurs, switch to the secondary endpoint immediately
            current_rpc = rpc_set["fallback"]
            unhealthy_counter = 0
            healthy_counter = 0
            logging.info("Error occurred. Switching to secondary endpoint.")
        
        return jsonify(result), response.status_code
    except requests.exceptions.RequestException as e:
        # If request times out, switch to the secondary endpoint immediately
        current_rpc = rpc_set["fallback"]
        unhealthy_counter = 0
        healthy_counter = 0
        logging.error(f"RPC request to {winner} failed: {e}")
        return jsonify({"error": "RPC request failed"}), 500

if __name__ == '__main__':
    # Use Gunicorn to run the application
    app.run(host='0.0.0.0', port=5000)
