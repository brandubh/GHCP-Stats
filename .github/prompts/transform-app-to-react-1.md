# Transform the Current Application to a React + FastAPI Architecture

Follow the steps below to guide the migration:

1. **Audit the Existing Codebase**  
   - List all current features, endpoints, and chart components.  
   - Identify data models, database schema, and external integrations.

2. **Define the Target Architecture**  
   - Front-end: React (Vite + TypeScript, TailwindCSS).  
   - Back-end: FastAPI (Python 3.10+, async, Pydantic).  
   - Databases:  
     • Local → SQLite (file-based, dev only).  
     • Azure → Azure Database for PostgreSQL.  
   - Deployment: Azure Container Apps (ACA) with separate containers for FE and BE.

3. **Set Up Development Environments**  
   - FE: `npm create vite@latest`, choose React + TS template.  
   - BE: `rye init`, add `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `asyncpg`, `pydantic-settings`.  
   - Create `.env` files for local and cloud configurations.

4. **Model & API Layer Refactoring**  
   - Convert existing ORM models to SQLAlchemy 2.0.  
   - Expose each existing feature through FastAPI routers (`/api/v1/…`).  
   - Add dependency to switch DB URL via environment variables.

5. **Front-End Migration**  
   - Replicate current pages using React functional components.  
   - Integrate charts with `react-chartjs-2` or `recharts` maintaining current visualizations.  
   - Add a responsive navbar; place a **Login** button at the top-right.

6. **Authentication Strategy**  
   - Implement JWT-based auth in FastAPI (`fastapi-users` or custom).  
   - FE: handle auth flow with React Context and `react-router-dom`, keep EntraID authentication.

7. **Local Development Workflow**  
   - Docker Compose with two services: `api` (FastAPI) and `web` (React), plus `db` (SQLite volume).  
   - Hot-reload enabled (`--reload` for FastAPI, `vite` for React).

8. **Azure Deployment Steps**  
   - Build multi-arch images with `docker buildx`.  
   - Push to Azure Container Registry.  
   - Provision ACA environments (one for BE, one for FE) using Bicep.  
   - Configure ACA secrets for DB credentials; bind to Azure PostgreSQL.

9. **CI/CD Pipeline**  
   - GitHub Actions:  
     • Lint & test (pytest, Ruff).  
     • Build & push images.  
     • Deploy to ACA with `azure/CLI` action.

10. **Validation & Handover**  
    - Execute regression tests ensuring feature parity.  
    - Document local vs. cloud launch commands.  
    - Update README and architecture diagram.
