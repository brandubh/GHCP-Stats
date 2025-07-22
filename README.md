# GHCP-Stats

GHCP-Stats is a small Streamlit application that imports GitHub Copilot metrics and visualises them in a web dashboard. Data is retrieved from the GitHub API, stored in a local SQLite database and displayed using interactive charts.

The project was generated with the help of GitHub Copilot and is meant as an experiment in AI assisted development.

## Repository layout

```
app/            # containerised application
  Dockerfile    # container definition
  requirements.txt
  src/          # Streamlit source code
infrastructure/ # Azure deployment scripts and Bicep templates
 docs/          # project documentation
```

The application itself lives under `app/src` and is composed of a few Streamlit pages and some helper utilities for authentication and data import.

## Quick start

### Local execution

1. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```
2. Set the environment variables `ORG_LIST` (comma separated organisation names) and `GHCP_TOKEN` (GitHub token with access to the metrics API). Optionally set `DB_NAME` to the desired SQLite path.
3. Run the application:
   ```bash
   streamlit run app/src/app.py
   ```

### Container

A `Dockerfile` is provided for container execution:

```bash
docker build -t ghcp-stats ./app
docker run -p 8501:8501 -e ORG_LIST=org -e GHCP_TOKEN=token ghcp-stats
```

### Azure deployment

Infrastructure templates for Azure Container Apps are located in the `infrastructure` folder. Deploy using `deploy.sh` and provide the required parameters and secrets.

See the documentation in the `docs/` folder for a detailed description of the configuration and deployment process.

## License

This project is released under the AGPL-3.0 license.
