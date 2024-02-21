# RPC Failover with Gunicorn - README

This project implements a Flask-based RPC failover system using Gunicorn as a WSGI HTTP server. It allows for automatic switching between primary and fallback RPC endpoints based on health checks. Further reversed proxy may be implemented.

## Features

- Automatic failover between primary and fallback RPC endpoints.
- Periodic health checks to monitor the availability of primary RPC endpoints.
- Seamless integration with Gunicorn for serving the Flask application.
- Easily configurable through Flask script.

## Prerequisites

- Python 3.x installed on your system.
- Flask and Gunicorn installed. You can install them using pip:

pip install flask gunicorn


## Configuration

1. Open the provided Flask script (`rpc_failover.py`) in a text editor.
2. Modify the `rpc_sets` variable to define your primary and fallback RPC endpoints. Each set should contain a `"primary"` and a `"fallback"` key with corresponding HTTPS addresses.
3. Optionally adjust the `timeout_threshold` and `minutes_threshold` variables to set the timeout and health check intervals, respectively.

## Running the Application

1. Configure and start the Gunicorn service using the provided service file (`gunicorn.service`).
   - Copy the provided service file to `/etc/systemd/system/` directory.
   - Ensure the Flask script (`rpc_failover.py`) is located in the specified working directory in the service file.
   - Reload systemd to apply the changes:

     ```
     sudo systemctl daemon-reload
     ```

   - Start and enable the Gunicorn service:

     ```
     sudo systemctl start gunicorn
     sudo systemctl enable gunicorn
     ```

## Sending RPC Requests

- Send POST requests to `http://localhost:5000/rpc` for example for set 0 send posts to: http://localhost:5000/rpc?rpc_set_index=0 for set 1 send requests to: http://localhost:5000/rpc?rpc_set_index=0 to access the RPC functionality.
- Include JSON data in the request body.
- Optionally, include the query parameter `rpc_set_index` to specify the RPC set index.

## Monitoring

- The application periodically checks the health of the primary RPC endpoints.
- If a primary endpoint fails, the system automatically switches to the fallback endpoint.
- Health status and endpoint switching are logged to the console.

## Notes

- Ensure that the primary and fallback RPC endpoints are correctly configured and accessible.
- Monitor the console output for any errors or status updates regarding RPC endpoint health and failover events.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).
