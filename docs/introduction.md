# Summary

This documentation is divided into the following sections:

1. [Introduction](introduction.md)
2. [Dependencies](dependencies.md)
3. [Solution Overview](solution-overview.md)
4. [Architecture](architecture.md)
5. [Data Architecture](data-architecture.md)
6. [Configuration](configuration.md)
7. [Monitoring](monitoring.md)
8. [Security](security.md)
9. [Deployment](deployment.md)
10. [Versioning](versioning.md)
11. [References](references.md)

# Introduction to GHCP-Stats

GHCP-Stats collects GitHub Copilot metrics for a list of organisations and displays the aggregated data in a Streamlit dashboard. Metrics are fetched using the GitHub REST API and persisted locally in a SQLite database. The application supports Azure AD authentication and can be containerised for deployment to Azure Container Apps.

