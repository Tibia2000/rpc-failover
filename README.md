
# RPC Failover with Gunicorn - README

This project implements a Flask-based RPC failover system using Gunicorn as a WSGI HTTP server. It allows for automatic switching between primary and fallback RPC endpoints based on health checks.

## Features


Periodic health checks for the primary endpoint.
Dynamic failover between primary and secondary endpoints based on health status.
Monitoring of regular RPC calls for errors and error messages.
Switching back to the primary endpoint after it has been healthy for a specified duration (minutes_threshold).


## Failover logic

Periodic Health Check for Primary Endpoint:

The periodically_check_primary_health function is responsible for periodically checking the health status of the primary endpoint.
This function continuously runs in a separate thread and executes health checks for the primary endpoint at regular intervals.
If the primary endpoint is found to be unhealthy or unreachable, the script switches to using the secondary endpoint.
Failover Logic:

If the primary endpoint fails the periodic health check, the script switches to using the secondary endpoint.
After failing over to the secondary endpoint, the script continues to periodically check the health status of the primary endpoint in the background.
If the primary endpoint becomes healthy again, the script switches back to using the primary endpoint for subsequent requests.
Health Check for Secondary Endpoint:

Periodic Health Checks:

The is_rpc_healthy function is used for the periodic health checks to determine if the RPC endpoint is healthy based on criteria such as block numbers changing and absence of error messages in the response.
These periodic health checks are performed independently of incoming RPC requests and are executed at regular intervals to continuously monitor the health of the RPC endpoint.
Regular RPC Calls:

When handling each individual RPC request in the proxy_rpc_request function, the response is checked for errors and error messages using the check_json_error function.
If an error is detected in the response of a regular RPC call, the script may switch to using the secondary RPC endpoint depending on the failover logic.
By combining periodic health checks with the monitoring of regular RPC calls for errors and error messages, the script provides comprehensive health monitoring and failover capabilities to ensure reliable operation of the RPC service.

## Prerequisites

- Python 3.x installed on your system.
- Flask and Gunicorn installed. You can install them using pip:

```
pip install flask gunicorn
add permission for log file
chmod 777 /var/log/rpc_failover

```

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

2. Set the addresses to call the RPC endpoints in your application code. For example, for Set 1, the address would be:

   ```
   http://localhost:5000/rpc?rpc_set_index=0
   ```

## Sending RPC Requests

- Send POST requests to `http://localhost:5000/rpc` to access the RPC functionality.
- Include JSON data in the request body.
- Optionally, include the query parameter `rpc_set_index` to specify the RPC set index.

## Monitoring

- The application periodically checks the health of the primary RPC endpoints.
- If a primary endpoint fails, the system automatically switches to the fallback endpoint.
- Health status and endpoint switching are logged to the `/var/log/rpc_failover.log` file.

## Notes

- Ensure that the primary and fallback RPC endpoints are correctly configured and accessible.
- Monitor the log file for any errors or status updates regarding RPC endpoint health and failover events.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).
```
