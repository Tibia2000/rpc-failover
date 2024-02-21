
# RPC Failover with Gunicorn - README

This project implements a Flask-based RPC failover system using Gunicorn as a WSGI HTTP server. It allows for automatic switching between primary and fallback RPC endpoints based on health checks.

## Features


Periodic health checks for the primary endpoint.
Dynamic failover between primary and secondary endpoints based on health status.
Monitoring of regular RPC calls for errors and error messages.
Switching back to the primary endpoint after it has been healthy for a specified duration (minutes_threshold).
## Failover logic v1.1

In the provided script, the failover mechanism allows switching back to the primary endpoint after it has been healthy for a specified duration. This duration is controlled by the minutes_threshold variable, which represents the minimum amount of time the primary endpoint must remain healthy before switching back to it.

Here's how the script determines when to switch back to the primary endpoint:

Primary Endpoint Health Check:

The script continuously monitors the health status of the primary endpoint using the periodically_check_primary_health function.
If the primary endpoint is found to be healthy during the periodic health check and has been unhealthy for at least the specified minutes_threshold, the script triggers a switch back to the primary endpoint.
Switch Back to Primary Endpoint:

Once the primary endpoint has been healthy for at least the specified duration (minutes_threshold), the script switches back to using the primary endpoint for subsequent requests.
After switching back to the primary endpoint, the script continues to monitor its health status to ensure continued reliability of the service.
By implementing this mechanism, the script ensures that the primary endpoint is given a grace period to stabilize and demonstrate sustained health before resuming normal operation. This approach helps prevent rapid toggling between primary and secondary endpoints, providing a more stable and reliable failover strategy.

## Prerequisites

- Python 3.x installed on your system.
- Flask and Gunicorn installed. You can install them using pip:

```
pip install flask gunicorn
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
