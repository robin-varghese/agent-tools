from flask import Flask, request, jsonify
from google.cloud import compute_v1
from google.auth import default
from typing import Dict, List
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_compute_engine_instances(config: Dict[str, str]) -> List[compute_v1.Instance]:
    # Initialize Google Cloud credentials and the Compute Engine API client
    credentials, default_project_id = default()
    compute_client = compute_v1.InstancesClient(credentials=credentials)
    """Retrieves a list of Compute Engine instances for a given domain, optionally filtered by project and zone.

    Args:
        config: A dictionary containing the configuration parameters. Required keys: - domain: The domain to filter instances by. Optional keys: - project_id: The ID of the Google Cloud project. - zone: The zone to filter instances by.

    Returns:
        A list of Compute Engine instance objects.
    """

    # Extract domain, project_id, and zone from config; use defaults or raise error if necessary
    domain = config.get('domain')
    project_id = config.get('project_id')
    zone = config.get('zone')

    if not domain:
        raise ValueError("Domain must be specified in the config.")
    if not project_id:
        project_id = default_project_id
        logger.info(f"Using default project_id: {project_id}")
    
    instances = []  # Initialize instances list
    try:
        if zone:  # If zone is specified, list instances in that zone
            logger.info(f"Fetching instances in project: {project_id}, zone: {zone} for domain: {domain}")
            request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
            logger.info(f"Requesting instances in project: {request}")
            agg_instances = compute_client.list(request=request)
            logger.info(f"agg_instances fetched: {agg_instances}")
            for instance in agg_instances:
                if instance.name.endswith(domain):
                    instances.append(instance)
        else:  # Otherwise, list instances across all zones
            logger.info(f"Fetching instances in all zones for project: {project_id} with domain: {domain}")
            request = compute_v1.AggregatedListInstancesRequest(project=project_id)
            logger.info(f"Requesting instances in project: {request}")
            agg_instances = compute_client.aggregated_list(request=request)
            logger.info(f"agg_instances fetched: {agg_instances}")
            for zone_name, response in agg_instances:
                if response.instances:
                    for instance in response.instances:
                        if instance.name.endswith(domain):
                            instances.append(instance)
        logger.info(f"Found {len(instances)} instances matching domain: {domain}")
        return instances
    except Exception as e:
        logger.error(f"Error fetching instances: {e}")
        raise


@app.route('/', methods=['GET'])
def hello_world():
    """A simple Hello World route."""
    name = request.args.get("name", "World")
    return f"Hello, {name}!"


@app.route('/list_vms', methods=['POST'])
def get_instances():
    """API endpoint to list Compute Engine instances."""
    logger.info("Received request at /list_vms")
    try:
        # Parse JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Call the function to retrieve instances based on the provided data.
        instances = get_compute_engine_instances(data)

        # Format the instance data to include only necessary information (name, zone, machine_type, status).
        instance_list = [{'name': instance.name,
                          'zone': instance.zone.split('/')[-1],  # Extract zone name from URL
                          'machine_type': instance.machine_type.split('/')[-1],  # Extract machine type from URL
                          'status': instance.status}
                         for instance in instances]

        logger.info(f"Returning {len(instance_list)} instances.")
        return jsonify({'instances': instance_list}), 200
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception("An unexpected error occurred.")  # Use logger.exception for detailed error info
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
