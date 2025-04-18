from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient import discovery
import os

app = Flask(__name__)


def get_compute_engine_instances(domain):
    """Retrieves a list of Compute Engine instances for a given domain."""
    # TODO: Implement the logic to fetch instances using the Compute Engine API
    return []


@app.route('/', methods=['GET'])
def hello_world():
    """Example Hello World route."""
    name = request.args.get("name", "World")  # Get 'name' from request arguments
    return f"Hello {name}!"


@app.route('/list_vms', methods=['POST'])
def list_vms():
    """API endpoint to list VMs in a domain."""
    data = request.get_json()
    if not data or 'domain' not in data:
        return jsonify({'error': 'Please provide a domain in the request body.'}), 400

    domain = data['domain']
    try:
        instances = get_compute_engine_instances(domain)
        return jsonify({'instances': instances})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

