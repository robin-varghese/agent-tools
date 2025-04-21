# Flask API Service Starter

This is a minimal Flask API service starter based on [Google Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service).

## Getting Started

Server should run automatically when starting a workspace. To run manually, run:
```sh
./devserver.sh
```
   46  gcloud run deploy list-vms --source . --project=vector-search-poc --region=us-central1
   47  curl -X POST -H "Content-Type: application/json" -d '{"domain": "your-domain.com"}' https://list-vms-qcdyf5u6mq-uc.a.run.app/list_vms
   48  curl -X POST -H "Content-Type: application/json" -d '{"domain": "cloudroaster.com"}' https://list-vms-qcdyf5u6mq-uc.a.run.app/list_vms
   49  curl -X POST -H "Content-Type: application/json" -d '{"domain": "cloudroaster.com","project_id":"vector-search-poc","zone":"us-central1-c"}' https://list-vms-qcdyf5u6mq-uc.a.run.app/list_vms
   50  gcloud run deploy list-vms --source . --project=vector-search-poc --region=us-central1
   51  curl -X POST -H "Content-Type: application/json" -d '{"domain": "cloudroaster.com","project_id":"vector-search-poc","zone":"us-central1-c"}' https://list-vms-qcdyf5u6mq-uc.a.run.app/list_vms
   52  curl -X POST -H "Content-Type: application/json" -d '{"domain": "your-domain.com"}' https://list-vms-qcdyf5u6mq-uc.a.run.app/list_vms
   53  curl -X POST -H "Content-Type: application/json" -d '{"domain": "cloudroaster.com","project_id":"vector-search-poc","zone":"us-central1-c"}' https://list-vms-qcdyf5u6mq-uc.a.run.app/list_vms
   54  curl -X POST -H "Content-Type: application/json" -d '{"domain": "your-domain.com"}' https://list-vms-qcdyf5u6mq-uc.a.run.app/list_vms