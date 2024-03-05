import logging
from flask import Flask, request, jsonify
import requests
import threading
import time

# Configure logging
logging.basicConfig(filename='/var/log/rpc_failover.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define your sets of primary and fallback RPC endpoints
rpc_sets = [
    {"primary": "https://", "fallback": "https://"},
    {"primary": "https://", "fallback": "https://"},
    {"primary": "https://", "fallback": "https://"},
    {"primary": "https://", "fallback": "https://"},
    {"primary": "https://", "fallback": "https://"},
]

# Add a global variable to store the currently selected RPC and counters
current_rpc = None  # Initialize current_rpc with the primary endpoint of the first RPC set
unhealthy_counter = 0
healthy_counter = 0
timeout_threshold = 15  # Set the timeout threshold in seconds
minutes_threshold = 1  # Set the minutes threshold

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

def switch_to_fallback(rpc_set):
    global current_rpc, unhealthy_counter, healthy_counter
    if current_rpc != rpc_set["fallback"]:
        current_rpc = rpc_set["fallback"]
        unhealthy_counter = 0
        healthy_counter = 0
        logging.info("Switching to fallback endpoint.")

def switch_to_primary(rpc_set):
    global current_rpc
    if current_rpc != rpc_set["primary"]:
        current_rpc = rpc_set["primary"]
        logging.info("Switching back to primary endpoint.2")

def periodically_check_primary_health():
    global current_rpc, unhealthy_counter, healthy_counter
    while True:
        for rpc_set in rpc_sets:  # Iterate through each set of RPC endpoints
            if current_rpc == rpc_set["primary"]:
                if not is_rpc_healthy(current_rpc):
                    unhealthy_counter += 1
                    if unhealthy_counter >= timeout_threshold:
                        switch_to_fallback(rpc_set)
                else:
                    if not is_block_number_updated(current_rpc):
                        switch_to_fallback(rpc_set)
                    else:
                        healthy_counter += 1
                        if healthy_counter >= 2 * minutes_threshold:
                            healthy_counter = 0  # Reset healthy counter
                            logging.info("Primary RPC is healthy and block number is updating.")
            elif current_rpc == rpc_set["fallback"]:
                if is_rpc_healthy(rpc_set["primary"]):
                    switch_to_primary(rpc_set)
                    logging.info("Switching back to primary endpoint.1")
        logging.debug(f"Current RPC: {current_rpc}, Unhealthy Counter: {unhealthy_counter}, Healthy Counter: {healthy_counter}")
        time.sleep(60)

# Start the periodic health check in a separate thread
health_check_thread = threading.Thread(target=periodically_check_primary_health)
health_check_thread.start()

def fetch_rpc_url_winner(rpc_set):
    global current_rpc
    # Choose the winner based on the current RPC
    winner = current_rpc if current_rpc else rpc_set["primary"]
    if current_rpc != rpc_set["primary"]:
        switch_to_primary(rpc_set)
    return winner, current_rpc

@app.route('/rpc', methods=['POST'])
def proxy_rpc_request():
    json_data = request.get_json()

    # Extract the RPC set index from the incoming request
    rpc_set_index = int(request.args.get('rpc_set_index', 0))
    rpc_set = rpc_sets[rpc_set_index]

    # Choose the RPC endpoint using the fetch_rpc_url_winner logic
    winner, selected_rpc = fetch_rpc_url_winner(rpc_set)

    # Log which RPC endpoint is used before sending the request
    logging.info("Sending RPC request to %s for RPC set: %s", selected_rpc, rpc_set)

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
