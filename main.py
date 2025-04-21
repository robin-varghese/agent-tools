from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient import discovery
import os
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
        logger.error("Domain must be specified in the config.")
        raise ValueError("Domain must be specified in the config")
    if not project_id:
        project_id = default_project_id
        logger.info(f"Using default project_id: {project_id}")
    
    instances = []  # Initialize instances list
    try:
        if zone:
            logger.info(f"Fetching instances in project: {project_id}, zone: {zone} for domain: {domain}")
            request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
            logger.info(f"Requesting instances in project: {request}")
            agg_instances = compute_client.list(request=request)
            #logger.info(f"agg_instances fetched: {agg_instances}")
            for instance in agg_instances:                
                logger.info(f"Checking instance: {instance.name} against domain: {domain}")
                if instance.name is not None:
                    instances.append(instance)
        else:
            logger.info(f"Fetching instances in all zones for project: {project_id} with domain: {domain}")
            request = compute_v1.AggregatedListInstancesRequest(project=project_id)
            logger.info(f"Requesting instances in project: {request}")
            agg_instances = compute_client.aggregated_list(request=request)
            #logger.info(f"agg_instances fetched: {agg_instances}")
            for zone_name, response in agg_instances:
                if response.instances:                    
                    for instance in response.instances:
                        logger.info(f"Checking instance: {instance.name} against domain: {domain}")
                        if instance.name is not None:
                            instances.append(instance)
        logger.info(f"Found {len(instances)} instances")
        # Format the instance data to include only necessary information (name, zone, machine_type, status).
        instance_list = [{'name': instance.name,
                          'zone': instance.zone.split('/')[-1],  # Extract zone name from URL
                          'machine_type': instance.machine_type.split('/')[-1],  # Extract machine type from URL
                          'status': instance.status}
                         for instance in instances]
        logger.info(f"Returning instances: {instance_list}")
        return  instance_list
    except Exception as e:
        logger.error(f"Error fetching instances: {e}")
        raise
def get_compute_engine_instances(config: Dict[str, str]) -> List[dict]:
    # Initialize Google Cloud credentials and the Compute Engine API client.
    credentials, default_project_id = default()
    compute_client = compute_v1.InstancesClient(credentials=credentials)
    """Retrieves a list of Compute Engine instances for a given domain,
    optionally filtered by project and zone.

    Args:
        config: A dictionary containing the configuration parameters.
            Required keys:
                - domain: The domain to filter instances by.
            Optional keys:
                - project_id: The ID of the Google Cloud project.
                - zone: The zone to filter instances by.

    Returns:
        A list of Compute Engine instance objects.
    """
    logging.info("Entering get_compute_engine_instances")
    logging.info(f"Config: {config}")

    # Extract the domain from the config; raise an error if not provided.
    domain = config.get("domain")
    if not domain:
        logging.error("Domain not provided in config")
        raise ValueError("The 'domain' key is required in the config dictionary.")

    # Determine the project ID; use the provided one or the default.
    project_id = config.get("project_id") or default_project_id
    logging.info(f"Using project_id: {project_id}")

    # Get the zone from the config, if provided.
    zone = config.get("zone")
    logging.info(f"Zone: {zone}")

    # Prepare the request to list instances. If a zone is specified, list instances in that zone.
    # Otherwise, list instances across all zones in the project.
    if zone:
        logging.info(f"Listing instances in zone: {zone}")
        request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
    else:
        logging.info("Listing instances across all zones")
        request = compute_v1.AggregatedListInstancesRequest(project=project_id)

    instances = []
    # Process the list of instances based on whether a specific zone was requested.
    if zone:
        logging.info("Processing instances from a specific zone")
        page_result = compute_client.list(request=request)
        for response in page_result:
            # Filter instances by the domain.
            for instance in response.items:
                logging.info(f"Checking instance: {instance.name}, Domain: {domain}")
                if instance.name is not None:
                    instances.append({
                        'name': instance.name,
                        'zone': instance.zone,
                        'machine_type': instance.machine_type,
                        'status': instance.status
                    })
    # If no specific zone was requested, iterate through all zones.
    else:
        logging.info("Processing instances across all zones")
        page_result = compute_client.aggregated_list(request=request)
        for zone, response in page_result.items():
            if response.instances:
                for instance in response.instances:
                    logging.info(f"Checking instance: {instance.name}, Domain: {domain}")
                    if instance.name is not None:
                        instances.append({
                            'name': instance.name,
                            'zone': instance.zone,
                            'machine_type': instance.machine_type,
                            'status': instance.status
                        })

    logging.info(f"Returning {len(instances)} instances")
    logging.info("Exiting get_compute_engine_instances")
    return instances
def delete_compute_engine_instance(project_id: str, instance_id: str, zone: str) -> bool:
    """Deletes a Google Compute Engine instance.

    Args:
        project_id: The ID of the Google Cloud project.
        instance_id: The ID of the Compute Engine instance to delete.
        zone: The zone where the instance is located.

    Returns:
        True if the instance was successfully deleted, False otherwise.
    """
    try:
        client = compute_v1.InstancesClient()
        req = compute_v1.DeleteInstanceRequest(
            project=project_id, zone=zone, instance=instance_id
        )
        client.delete(req)
        logging.info(
            f"Successfully deleted instance {instance_id} in project {project_id} and zone {zone}."
        )
        return True
    except Exception as e:
        logging.error(
            f"Error deleting instance {instance_id} in project {project_id} and zone {zone}: {e}"
        )
        return False


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

        logger.info(f"Returning {len(instances)} instances.")
        return jsonify({'instances': instances}), 200
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception("An unexpected error occurred.")  # Use logger.exception for detailed error info
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500

@app.route('/delete_vms', methods=['POST'])
def delete_instances():
    """API endpoint to delete Compute Engine instances."""
    json_results = []  # Initialize json_results here
    try:
        data = request.get_json()
        if not data or 'project_id' not in data or 'instance_id' not in data:
            return jsonify({'error': 'Invalid request format. Missing project_id or instance_id.'}), 400

        project_id = data['project_id']
        instance_id = data['instance_id']
        zone = data['zone']
        logging.info(f"Attempting to delete instances in project={project_id} in zone={zone} instanceid= {instance_id}.")
        #zone = data.get('zone', "us-central1-a")  # Get zone from request, default to "us-central1-a"

        if isinstance(instance_id, str) and instance_id == "ALL":
            # Handle wildcard deletion (delete all instances)
            logging.info(f"Attempting to delete ALL instances in project {project_id} in zone {zone}.")
            # In a real scenario, you would first list all instances and then delete them.
            return jsonify({'message': f'Attempting to delete ALL instances in project {project_id} in zone {zone}.  (Listing and deletion of all instances needs to be implemented)'}), 200  # Indicate success for now, as the logic isn't fully implemented here
        elif isinstance(instance_id, str):
            logging.info(f"Attempting to delete one instances in project {project_id} in zone {zone}.")
            results = delete_compute_engine_instance(project_id, instance_id, zone)
            #for instance_id in instance_id:
            if delete_compute_engine_instance(project_id, instance_id, zone):
                json_results.append({'instance_id': instance_id, 'status': 'deleted'})
            else:
                json_results.append({'instance_id': instance_id, 'status': 'failed'})
            return jsonify({'results': json_results}), 200
        else:
            return jsonify({'error': 'Invalid instance_id format. Use a list of IDs or "ALL".'}), 400
    except Exception as e:
        logging.exception("Error processing delete request.")
        return jsonify({'error': f'Error processing request: {e}'}), 500
