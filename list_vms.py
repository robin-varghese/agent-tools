from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient import discovery
import os

app = Flask(__name__)

def get_compute_engine_instances(domain):
    """Retrieves a list of Compute Engine instances for a given domain."""
    try:
        # Attempt to get project ID from environment (assuming this environment 
        # has a default project configured).  If not available, you'd need to 
        # handle project selection differently (e.g., require it as input).
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")  
        if not project:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set. Cannot determine project.")
        
        # Use Application Default Credentials (ADC) or a service account
        credentials, _ = google.auth.default()
        
        compute = discovery.build('compute', 'v1', credentials=credentials)

        instances = []
        # In this environment, we can only list instances within the current project.
        # For cross-organization queries, more extensive permissions and different 
        # tooling (e.g., gcloud CLI with organization-level access) would be needed.
        req = compute.instances().list(project=project, zone='us-central1-a') # Replace 'us-central1-a' with your desired zone or remove for all zones in region
        while req is not None:
            resp = req.execute()
            if 'items' in resp:
                for instance in resp['items']:
                    instances.append({
                        'name': instance['name'],
                        'zone': instance['zone'].split('/')[-1],
                        'status': instance['status'],
                        # Add other relevant instance details as needed
                    })
            req = compute.instances().list_next(req, resp)
        return instances
    except Exception as e:
        raise Exception(f"Error retrieving instances: {str(e)}. Ensure your service account has the 'compute.instances.list' permission in the project, and that the GOOGLE_CLOUD_PROJECT environment variable is set correctly if relying on ADC.")


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

if __name__ == '__main__':
    import google.auth

    # The following code attempts to detect if the environment is Google Cloud 
    # and uses the port provided by the environment, otherwise it defaults to 8080.
    if os.environ.get("GOOGLE_CLOUD_PROJECT"):
        app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    else:
        app.run(debug=True, host='0.0.0.0', port=8080)