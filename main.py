from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient import discovery
import os
from google.cloud import compute_v1
from google.auth import default
from typing import Dict, List, Any
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_compute_engine_instances(project_id: str, zone:str) -> List[Dict[str, Any]]: # Updated return type hint
    """
    Retrieves all GCE instances in a project and returns them as a list of dictionaries.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.

    Returns:
        A list where each item is a dictionary containing details for one instance, e.g.:
        {
            "project_id": "your-project-id",
            "zone": "us-central1-c",
            "instance_id": "instance-name-1",
            "machine_type": "n2-standard-2"
        }
    """
    instance_client = compute_v1.InstancesClient()
    request = compute_v1.AggregatedListInstancesRequest()
    logger.info(f"Project ID: {project_id}")
    request.project = project_id
    #request.zone = zone
    
    # Use the `max_results` parameter to limit the number of results that the API returns per response page.
    # The client library handles pagination automatically regardless.
    request.max_results = 50

    agg_list = instance_client.aggregated_list(request=request)

    # Initialize an empty list to hold the instance dictionaries
    instances_list = []
    logger.info("Instances found:")

    # Iterate through zones and the responses containing instances for each zone
    for zone, response in agg_list:
        if response.instances:
            # Extract the short zone name (e.g., "us-central1-a" from "zones/us-central1-a")
            # Check if zone is not empty before splitting
            short_zone_name = zone.split('/')[-1] if zone else "unknown_zone"

            logger.info(f" {zone}:") # Keep console logging for info

            # Iterate through each instance found in the current zone
            for instance in response.instances:
                # Extract the short machine type name from the full URL path
                # e.g., "n2-standard-2" from ".../machineTypes/n2-standard-2"
                machine_type_name = instance.machine_type.split('/')[-1] if instance.machine_type else "unknown_type"

                logger.info(f" - {instance.name} ({machine_type_name})") # Keep console logging for info

                # Create the dictionary for the current instance
                instance_data = {
                    "project_id": project_id,
                    "zone": short_zone_name,
                    # Using instance name as ID. Use instance.id for the numerical ID if needed.
                    "instance_id": instance.name,
                    "machine_type": machine_type_name
                }
                # Add the dictionary to our results list
                instances_list.append(instance_data)
    logger.info(f"final list: {instances_list}");
    # Return the final list of dictionaries
    return instances_list

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
        project_id = data['project_id']
        zone = data['zone']
        logging.info(f"Attempting to list instances in project={project_id} in zone={zone}.")
        instances = get_compute_engine_instances(project_id,zone)

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
