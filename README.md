# GHCP-Stats

GHCP-Stats was originally a Streamlit application. It now uses a
**frontend/backend** architecture with **React** for the UI and **FastAPI** as
the server. The application runs against a local SQLite database for
development and automatically switches to Azure Cosmos DB when the `ENV`
environment variable is set to `azure`.

## Repository layout

```
backend/        # FastAPI backend
frontend/       # React frontend
infrastructure/ # Azure deployment scripts and Bicep templates
docs/          # project documentation
```

The backend code lives in `backend/` while the React frontend resides in
`frontend/`. A production Docker image bundles the compiled frontend together
with the FastAPI server so the app can be run anywhere with a single command.

## Quick start

### Local execution

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```
2. Set the environment variables `ORG_LIST` and `GHCP_TOKEN`. Optional variables:
   - `DB_NAME` – path to the SQLite database (defaults to `metrics.db`)
   - `ENV=azure` plus `COSMOS_ENDPOINT` and `COSMOS_KEY` when running in Azure
3. Run the backend and frontend during development:
   ```bash
   uvicorn backend.app.main:app --reload
   npm start
   ```

### Container

A root `Dockerfile` builds the React frontend and bundles it with the FastAPI
backend:

```bash
docker build -t ghcp-stats .
docker run -p 8000:8000 -e ORG_LIST=org -e GHCP_TOKEN=token ghcp-stats
```

### Azure deployment

Infrastructure templates for Azure Container Apps are located in the `infrastructure` folder. Deploy using `deploy.sh` and provide the required parameters and secrets.

When deployed with `ENV=azure` the backend connects to Cosmos DB using the
`COSMOS_ENDPOINT` and `COSMOS_KEY` variables. Locally these can be omitted to
fall back to SQLite.

See the documentation in the `docs/` folder for a detailed description of the configuration and deployment process.

## License

This project is released under the AGPL-3.0 license.
