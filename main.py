from flask import Flask, request, jsonify
from google.cloud import compute_v1
from google.auth import default
from typing import Dict, List
import os

app = Flask(__name__)


def get_compute_engine_instances(config: Dict[str, str]) -> List[compute_v1.Instance]:
    # Initialize Google Cloud credentials and the Compute Engine API client.
    credentials, default_project_id = default()
    compute_client = compute_v1.InstancesClient(credentials=credentials)
    """Retrieves a list of Compute Engine instances for a given domain, optionally filtered by project and zone.

    Args:
        config: A dictionary containing the configuration parameters. Required keys: - domain: The domain to filter instances by. Optional keys: - project_id: The ID of the Google Cloud project. - zone: The zone to filter instances by.

    Returns:
        A list of Compute Engine instance objects whose names end with the specified domain.
    """

    # Extract the domain from the config; raise an error if not provided.
    domain = config.get("domain")
    if not domain:
        raise ValueError("The 'domain' key is required in the config dictionary.")

    # Determine the project ID; use the provided one or the default.
    project_id = config.get("project_id") or default_project_id

    # Get the zone from the config, if provided.
    zone = config.get("zone")

    # Initialize an empty list to hold the instances.
    instances = []

    # If a specific zone is provided, list instances only in that zone.
    if zone:
        # Create a request object for listing instances in the specified zone.
        req = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
        # Use the client to list instances based on the request.
        page_result = compute_client.list(request=req)
    else:
        # If no specific zone is provided, list instances across all zones.
        req = compute_v1.AggregatedListInstancesRequest(project=project_id)
        # Use the client to list instances across all zones.
        page_result = compute_client.aggregated_list(request=req)

    # Iterate over the results (depending on whether the request was for a single zone or all zones).
    for items in page_result:
        # For single-zone requests, 'items' will be a list of instances.
        if isinstance(items, list):
            for instance in items:
                if instance.name.endswith(domain):
                    instances.append(instance)
        # For aggregated requests, 'items' will be a tuple (zone, response).
        elif isinstance(items, tuple) and len(items) == 2:
            zone, response = items
            if response.instances:
                for instance in response.instances:
                    if instance.name.endswith(domain):
                        instances.append(instance)

    return instances


@app.route('/', methods=['GET'])
def hello_world():
    """Example Hello World route."""
    name = request.args.get("name", "World")  # Get 'name' from request arguments
    return f"Hello {name}!"


@app.route("/list_vms", methods=["POST"])
def get_instances():
    # Define the API endpoint for retrieving Compute Engine instances.
    """
    API endpoint to retrieve Compute Engine instances based on domain, project_id, and zone.
    """
    try:
        # Attempt to parse JSON data from the request.
        data = request.get_json()
        # If no data is provided, return an error.
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Call the function to retrieve instances based on the provided data.
        instances = get_compute_engine_instances(data)

        # Format the instance data to include only necessary information (name, zone, machine_type, status).
        # This creates a simplified list of dictionaries for each instance.
        #instance_list = []
        #for instance in instances:
        #    instance_list.append({
        #        'name': instance.name,
        #        'zone': instance.zone,
        #        'machine_type': instance.machine_type,
        #        'status': instance.status
        #    })
        instance_list = [
            {
                "name": instance.name,
                "zone": instance.zone.split("/")[-1],  # Extract zone name from URL
                "machine_type": instance.machine_type.split("/")[-1],  # Extract machine type from URL
                "status": instance.status,
            }
            for instance in instances
        ]

        # Return the list of instances as a JSON response with a 200 OK status.
        return jsonify({"instances": instance_list}), 200
    # Handle potential ValueErrors (e.g., missing 'domain' in the request).
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    # Handle any other exceptions that might occur during the process.
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
        
