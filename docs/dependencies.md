# Dependencies

## External Systems

GHCP-Stats integrates with the following external systems:

- **GitHub Copilot API**: The application connects to GitHub's Copilot metrics API to retrieve usage statistics for organizations.
- **Azure Authentication**: Uses Microsoft Entra ID (formerly Azure AD) for user authentication.
- **Azure Key Vault**: Retrieves secrets securely in production environments.

## Libraries and Frameworks

### Core Application

- **Streamlit**: The primary web application framework used for building the interactive dashboard UI.
- **Python**: The application is written in Python, serving as both the backend and frontend technology.

### Data Processing and Storage

- **SQLite**: Used as the database for storing GitHub Copilot metrics data.
- **Pandas**: Employed for data manipulation, analysis, and preparation for visualization.
- **NumPy**: Utilized for numerical operations and data transformations.

### API Communication

- **Requests**: Handles HTTP requests to the GitHub Copilot API endpoints.
- **JSON**: Used for parsing API responses and storing structured data.

### Authentication & Security

- **MSAL (Microsoft Authentication Library)**: Manages authentication flows with Microsoft Entra ID.
- **dotenv**: Loads environment variables from .env files.
- **Azure Identity**: Used for accessing Azure Key Vault in production.

### Containerization & Deployment

- **Docker**: The application is containerized for deployment.
- **Azure Bicep**: Used for Infrastructure as Code (IaC) deployment to Azure.

## Version Requirements

| Dependency           | Required Version | Notes                                      |
|----------------------|------------------|-------------------------------------------|
| Python               | 3.8+             | Application runtime                        |
| Streamlit            | Latest           | Web framework                              |
| SQLite               | 3.x              | Database engine                            |
| Docker               | Latest           | Containerization                           |
| Azure CLI            | Latest           | For deployment operations                  |
| GitHub API           | v2022-11-28      | Specified in API headers                   |

## Development Dependencies

- **Azure Bicep CLI**: For developing and testing infrastructure templates
- **jq**: Command-line JSON processor used in deployment scripts
- **Bash**: Shell environment for running deployment scripts

## Environment Setup

The complete list of Python dependencies can be found in the [requirements.txt](../app/requirements.txt) file. The application requires proper environment variables to be set as documented in the [configuration.md](configuration.md) file.

For local development:
```bash
pip install -r app/requirements.txt