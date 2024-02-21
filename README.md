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

