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

app = Flask(__name__)

# Configure logging to write to a file
log_file = '/var/log/rpc_failover.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your number of sets of primary and fallback RPC endpoints
rpc_sets = [
    {"primary": "https://arb-mai", "secondary": "https://arbitrum.blxxxxxxxxxxxxxxxxx"},
    {"primary": "https://arbixxxxxxxxxxxxxxxxxx", "secondary": "https://arb-maixxxxxxxxxxxxxxxU"},
]

# Add global variables to store the current RPC, counters, and last switch time
current_rpc = None
last_primary_health_time = None
timeout_threshold = 2  # Set the timeout threshold in seconds
minutes_threshold = 2  # Set the minutes threshold

def is_rpc_healthy(rpc_url):
    try:
        response = requests.post(rpc_url, json={"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",False],"id":1}, timeout=timeout_threshold)
        response.raise_for_status()
        blocks = response.json().get("result")
        if not blocks:
            return False  # No blocks returned
        # Check if block numbers are changing (indicating node is syncing)
        block_numbers = [int(block["number"], 16) for block in blocks]
        if len(set(block_numbers)) <= 1:
            return False  # Block numbers are not changing, indicating potential issue with node
        # Check if error or err key is present in the JSON response
        if 'error' in response.json() or 'err' in response.json():
            return False  # Error detected in JSON response
        return True  # RPC endpoint is healthy
    except requests.exceptions.RequestException:
        return False  # Request failed or timed out

def periodically_check_primary_health():
    global current_rpc, last_primary_health_time
    while True:
        if current_rpc == rpc_set["secondary"]:
            if is_rpc_healthy(rpc_set["primary"]):
                current_rpc = rpc_set["primary"]
                last_primary_health_time = time.time()  # Update last_primary_health_time when primary becomes healthy
                logging.info("Primary RPC endpoint is healthy. Switched back to primary.")
        elif current_rpc == rpc_set["primary"] and last_primary_health_time:
            if time.time() - last_primary_health_time >= minutes_threshold * 60:
                current_rpc = rpc_set["secondary"]
                logging.warning("Failover to secondary RPC endpoint: %s", rpc_set["secondary"])
        time.sleep(60)

# Start the periodic health check in a separate thread
health_check_thread = threading.Thread(target=periodically_check_primary_health)
health_check_thread.start()

@app.route('/rpc', methods=['POST'])
def proxy_rpc_request():
    global current_rpc
    json_data = request.get_json()

    # Extract the RPC set index from the incoming request
    rpc_set_index = int(request.args.get('rpc_set_index', 0))
    rpc_set = rpc_sets[rpc_set_index]

    try:
        response = requests.post(current_rpc, json=json_data)
        response.raise_for_status()
        if current_rpc == rpc_set["secondary"]:
            current_rpc = rpc_set["primary"]  # Switch back to primary if request was successful and using secondary
            logging.info("Switched back to primary RPC endpoint: %s", rpc_set["primary"])
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        error_message = f"RPC request to {current_rpc} failed: {e}"
        logging.error(error_message)
        if current_rpc == rpc_set["primary"]:
            current_rpc = rpc_set["secondary"]  # Switch to secondary if request failed on primary
            logging.warning("Switched to secondary RPC endpoint: %s", rpc_set["secondary"])
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    # Use Gunicorn to run the application
    app.run(host='0.0.0.0', port=5000)
