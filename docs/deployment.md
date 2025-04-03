# Deployment

## CI/CD Pipeline

GHCP-Stats employs a robust CI/CD pipeline to ensure efficient and reliable deployment of updates.

### Pipeline Stages

1. **Code Validation**:
   - Linting and formatting checks using `ruff`.
   - Static code analysis for security vulnerabilities.

2. **Unit Testing**:
   - Executes `pytest` to validate functionality and ensure high test coverage.

3. **Build and Package**:
   - Docker images are built using the `Dockerfile`.
   - Images are tagged with version numbers and pushed to a container registry (e.g., Azure Container Registry).

4. **Integration Testing**:
   - Runs end-to-end tests in a staging environment.

5. **Deployment**:
   - Automated deployment to development, staging, and production environments using `bicep` templates.

6. **Post-Deployment Validation**:
   - Health checks and smoke tests to verify successful deployment.

## Infrastructure Requirements

GHCP-Stats is designed to run on Azure infrastructure with the following requirements:

### Compute Resources
- **Application Servers**: Azure App Service or Azure Kubernetes Service (AKS).
- **Database**: Azure Cosmos DB (MongoDB API) for primary data storage.
- **Analytics**: Azure Synapse Analytics or Azure Data Explorer for analytical workloads.
- **Caching**: Azure Cache for Redis for in-memory caching.

### Networking
- **Load Balancer**: Azure Application Gateway for traffic distribution.
- **DNS**: Azure DNS for domain management.
- **Firewall**: Azure Firewall for network security.

### Storage
- **Blob Storage**: Azure Blob Storage for logs, reports, and backups.
- **File Storage**: Azure Files for shared configuration files.

### Monitoring and Logging
- **Azure Monitor**: For performance and health monitoring.
- **Log Analytics**: For centralized log management.

## Deployment Steps

### Prerequisites
1. Install the Azure CLI and log in to your Azure account.
2. Ensure the required Azure resources (e.g., resource groups, container registry) are provisioned.
3. Configure environment variables and secrets in Azure Key Vault.

### Deployment Process

1. **Build Docker Images**:
   ```bash
   docker build -t ghcp-stats:latest .
   docker tag ghcp-stats:latest <container-registry>/ghcp-stats:latest
   docker push <container-registry>/ghcp-stats:latest
   ```

2. **Deploy Infrastructure**:
   ```bash
   az deployment group create \
     --resource-group <resource-group> \
     --template-file infrastructure/main.bicep \
     --parameters @infrastructure/parameters.main.dev.json
   ```

3. **Deploy Application**:
   - Update the container image reference in the deployment configuration.
   - Apply the deployment using Azure Kubernetes Service (AKS) or Azure App Service.

4. **Run Post-Deployment Tests**:
   ```bash
   pytest tests/post_deployment
   ```

5. **Monitor Deployment**:
   - Use Azure Monitor and Log Analytics to verify application health and performance.

### Rollback Strategy

In case of deployment failure:
1. Revert to the previous stable Docker image:
   ```bash
   docker tag <container-registry>/ghcp-stats:<previous-version> <container-registry>/ghcp-stats:latest
   docker push <container-registry>/ghcp-stats:latest
   ```
2. Redeploy the application with the stable image.
3. Investigate and resolve the issue before attempting a new deployment.