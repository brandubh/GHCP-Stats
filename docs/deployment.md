# Deployment

A minimal Docker image can be built from the `app` directory:

```bash
docker build -t ghcp-stats ./app
```

Run the container locally with the required environment variables:

```bash
docker run -p 8501:8501 \
  -e ORG_LIST=my-org \
  -e GHCP_TOKEN=gh_token \
  ghcp-stats
```

The `infrastructure` folder contains Bicep templates and helper scripts to deploy the container image to Azure Container Apps. `deploy.sh` expects an Azure resource group and registry to already exist and requires the same environment variables used for local execution.
