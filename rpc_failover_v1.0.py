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
    {"primary": "https://arb-mai", "fallback": "https://arbitrum.blxxxxxxxxxxxxxxxxx"},
    {"primary": "https://arbixxxxxxxxxxxxxxxxxx", "fallback": "https://arb-maixxxxxxxxxxxxxxxU"},
]

# Add a global variable to store the currently selected RPC and counters
current_rpc = None
unhealthy_counter = 0
healthy_counter = 0
timeout_threshold = 2  # Set the timeout threshold in seconds
minutes_threshold = 1  # Set the minutes threshold

def is_rpc_healthy(rpc_url):
    try:
        response = requests.get(rpc_url, timeout=1)  # Adjust timeout as needed
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
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
                    logging.warning("Failover to fallback RPC endpoint: %s", rpc_set["fallback"])
            else:
                healthy_counter += 1
                if healthy_counter >= minutes_threshold:
                    current_rpc = rpc_set["primary"]
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
        response = requests.post(winner, json=json_data)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logging.error("RPC request to %s failed: %s", winner, e)
        return jsonify({"error": "RPC request failed"}), 500

if __name__ == '__main__':
    # Use Gunicorn to run the application
    app.run(host='0.0.0.0', port=5000)
