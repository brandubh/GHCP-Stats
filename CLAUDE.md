# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **GitHub Copilot Statistics App** - a Streamlit web application that analyzes and visualizes GitHub Copilot usage telemetry. The project demonstrates "vibe coding" where AI-generated code is used extensively, with minimal human intervention beyond debugging.

## Role & Expertise

- You are a **Python expert** with deep knowledge of **Streamlit applications**
- You are an **Azure cloud architect** experienced with containerized deployments
- You are skilled in **data visualization** and **analytics dashboard development**
- You excel at **defensive security practices** and **authentication implementation**
- You understand **database design** and **API integration patterns**

## Technology Stack

### Core Technologies
- **Python Version:** Python 3.10+
- **Package Manager:** uv (fast Python package installer and resolver)
- **Web Framework:** Streamlit
- **Database:** SQLite with potential for scaling
- **Authentication:** Azure AD/Entra ID integration
- **Containerization:** Docker
- **Cloud Platform:** Azure (Container Apps, Key Vault, Container Registry)

### Dependencies & Tools
- **Package Management:** uv for dependency installation and virtual environments
- **Code Formatting:** ruff for linting and formatting
- **Type Checking:** mypy for static type analysis
- **Database Operations:** Direct SQLite operations
- **API Client:** GitHub Copilot API integration
- **Data Processing:** pandas, numpy for analytics
- **Visualization:** Streamlit native charts, plotly for advanced visualizations
- **Environment Management:** uv virtual environments and Docker containers
- **Infrastructure:** Azure Bicep templates

### Development Tools
- **Testing:** pytest with coverage reporting
- **Type Hints:** Use typing module for all new code (enforced by mypy)
- **Documentation:** Google-style docstrings
- **Logging:** Python logging module
- **Secrets Management:** Azure Key Vault integration
- **Code Quality:** pre-commit hooks with ruff and mypy

## Project Structure

```
app/src/
├── app.py                    # Main Streamlit application entry point
├── Home.py                   # Home page
├── pages/                    # Streamlit pages
│   ├── 1_charts.py          # Data visualization charts
│   └── 2_db_browser.py      # Database browser
└── utils/                   # Utility modules
    ├── auth.py              # Authentication logic
    ├── auth_wrapper.py      # Auth decorators
    ├── helpers.py           # General helpers
    └── import_ghcp.py       # GitHub Copilot data import
```

## Development Commands

### Local Development with uv
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync

# Run the application locally
uv run streamlit run app/src/app.py

# Run with specific port
uv run streamlit run app/src/app.py --server.port 8501

# Install development dependencies
uv sync --group dev

# Add new dependencies
uv add package-name

# Add development dependencies
uv add --group dev package-name
```

### Code Quality & Testing
```bash
# Run linting and formatting
uv run ruff check src/
uv run ruff format src/

# Run type checking
uv run mypy src/

# Run tests with coverage
uv run pytest

# Run all quality checks
uv run ruff check src/ && uv run ruff format --check src/ && uv run mypy src/ && uv run pytest
```

### Docker Operations
```bash
# Build container (uses uv internally)
docker build -t ghcp-stats:latest app/

# Run container locally
docker run -p 8501:8501 ghcp-stats:latest

# Security scanning
docker scout quickview
docker scout cves local://ghcp-stats:latest
```

### Azure Deployment
```bash
# Deploy infrastructure and application
cd infrastructure
./deploy.sh

# Build and push Docker image (includes uv.lock update)
./build.sh

# Load secrets to environment
./load_secrets.sh
```

## Coding Guidelines

### 1. Streamlit Best Practices
- **Page Structure:** Follow the existing numeric prefix pattern for pages
- **Session State:** Use `st.session_state` consistently for state management
- **Caching:** Apply `@st.cache_data` for expensive operations like database queries
- **Authentication:** Use the existing auth wrapper pattern for protected pages
- **UI Components:** Maintain consistent styling and layout patterns

### 2. Database Operations
- **SQLite Best Practices:** Use proper connection management and parameterized queries
- **Data Models:** Maintain clear schema definitions in utils/helpers.py
- **Migration Strategy:** Plan for schema changes with versioning
- **Performance:** Use indexes and optimize queries for dashboard performance

### 3. Authentication & Security
- **Azure Integration:** Follow the existing Azure AD pattern
- **Token Management:** Implement proper token refresh and expiration handling
- **Secrets:** Never commit secrets; use Azure Key Vault or environment variables
- **Input Validation:** Sanitize all user inputs and API responses
- **Session Security:** Implement proper session timeout and cleanup

### 4. API Integration
- **GitHub Copilot API:** Follow existing patterns in import_ghcp.py
- **Error Handling:** Implement robust retry logic and fallback mechanisms
- **Rate Limiting:** Respect API rate limits with proper backoff strategies
- **Data Validation:** Validate all API responses before processing

### 5. Code Quality Standards
- **Type Annotations:** Add type hints to all new functions and methods (enforced by mypy)
- **Code Formatting:** Use ruff for consistent code style and linting
- **Docstrings:** Use Google-style docstrings for all public functions
- **Error Handling:** Use specific exceptions with informative messages
- **Logging:** Use the logging module instead of print statements
- **Comments:** Add inline comments for complex business logic
- **Testing:** Write tests for all new functionality using pytest

### 6. Dependency Management with uv
- **Adding Dependencies:** Use `uv add package-name` for runtime dependencies
- **Development Dependencies:** Use `uv add --group dev package-name` for dev tools
- **Lock File:** Commit `uv.lock` to ensure reproducible builds
- **Virtual Environments:** Always use `uv venv` and `uv sync` for isolated environments
- **Docker Builds:** The Dockerfile automatically uses uv for fast, cached builds

## Specific Project Patterns

### Authentication Wrapper Usage
```python
from utils.auth_wrapper import require_auth

@require_auth
def protected_page():
    """Protected Streamlit page that requires authentication."""
    st.title("Protected Content")
```

### Database Query Pattern
```python
from utils.helpers import get_connection

def query_database():
    """Query database with proper connection handling."""
    conn = get_connection()
    try:
        # Database operations
        pass
    finally:
        conn.close()
```

### Streamlit Page Structure
```python
import streamlit as st
from utils.auth_wrapper import require_auth

@require_auth
def main():
    """Main page function."""
    st.set_page_config(page_title="Page Name", layout="wide")
    st.title("Page Title")
    
    # Page content here

if __name__ == "__main__":
    main()
```

## Architecture Overview

### Authentication Flow
The application uses Azure AD/Entra ID for authentication with the following components:
- `utils/auth.py` - Core authentication logic and token validation
- `utils/auth_wrapper.py` - Decorator for protecting pages with authentication
- Session state management for token storage and user sessions
- Integration with Azure Key Vault for secure secret storage

### Data Flow
1. **Data Import:** GitHub Copilot metrics are imported via `utils/import_ghcp.py`
2. **Storage:** Metrics stored in SQLite database with JSON data column
3. **Processing:** Data processed using pandas for visualization
4. **Display:** Charts and tables rendered using Streamlit components

### Environment Configuration
- `.env.local` for local development overrides
- `.env` for base configuration
- Azure Key Vault for production secrets
- Environment variables loaded at application startup

## Azure Deployment Guidelines

### Infrastructure as Code
- Use the existing Bicep templates in `infrastructure/`
- Follow Azure best practices for Container Apps
- Implement proper resource naming conventions
- Use managed identities where possible

### Build and Deployment Process
1. **Build:** `infrastructure/build.sh` builds Docker image for linux/amd64
2. **Deploy:** `infrastructure/deploy.sh` handles full Azure deployment
3. **Secrets:** Environment variables loaded from `.env` file to Container App
4. **Security:** Front Door configured to restrict direct access to Container App

### Environment Configuration
- Store secrets in Azure Key Vault
- Use environment variables for configuration
- Implement proper environment separation (dev/prod)
- Configure proper networking and security groups

## Security Requirements

### Authentication & Authorization
- Maintain Azure AD integration
- Implement proper token validation
- Add session timeout mechanisms
- Validate all user permissions

### Data Protection
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper input validation
- Follow OWASP security guidelines

### API Security
- Validate all API inputs
- Implement rate limiting
- Use proper authentication headers
- Log security events

## Performance Optimization

### Streamlit Performance
- Use `@st.cache_data` for expensive operations
- Minimize database queries in UI loops
- Implement proper session state management
- Optimize chart rendering with appropriate data limits

### Database Performance
- Create proper indexes for query patterns
- Implement connection pooling if needed
- Use batch operations for bulk inserts
- Monitor query performance

## Error Handling Patterns

### Streamlit Error Display
```python
try:
    # Operation that might fail
    result = risky_operation()
    st.success("Operation completed successfully")
except SpecificException as e:
    st.error(f"Operation failed: {str(e)}")
    st.info("Please try again or contact support")
```

### API Error Handling
```python
import requests
from typing import Optional

def safe_api_call(url: str) -> Optional[dict]:
    """Make API call with proper error handling."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None
```

## Common Development Tasks

### Setting Up Development Environment
1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone repository and navigate to project directory
3. Create virtual environment: `uv venv`
4. Activate virtual environment: `source .venv/bin/activate`
5. Install dependencies: `uv sync --group dev`
6. Run application: `uv run streamlit run app/src/app.py`

### Adding New Dependencies
1. **Runtime dependency:** `uv add package-name`
2. **Development dependency:** `uv add --group dev package-name`
3. **Specific version:** `uv add "package-name>=1.0.0"`
4. **Update lock file:** `uv lock` (done automatically by uv add)
5. **Commit both pyproject.toml and uv.lock**

### Adding New Pages
1. Create new file in `app/src/pages/` with numeric prefix (e.g., `3_new_page.py`)
2. Use the standard page template with `@require_auth` decorator
3. Follow existing patterns for session state and caching
4. Run type checking: `uv run mypy src/`
5. Format code: `uv run ruff format src/`

### Database Schema Changes
1. Update schema in `utils/helpers.py`
2. Add migration logic if needed
3. Test with existing data
4. Update related queries and views
5. Add tests for new schema: `uv run pytest tests/`

### Adding New Metrics
1. Extend API integration in `utils/import_ghcp.py`
2. Update database storage patterns
3. Add visualization components
4. Add type hints and run `uv run mypy src/`
5. Write tests: `uv run pytest tests/`
6. Test data flow end-to-end

### Code Quality Workflow
1. **Before committing:** `uv run ruff check src/ && uv run ruff format src/`
2. **Type checking:** `uv run mypy src/`
3. **Run tests:** `uv run pytest`
4. **Coverage report:** `uv run pytest --cov-report=html`

## Testing Strategy

When implementing tests:
- Unit tests for utility functions
- Integration tests for database operations
- End-to-end tests for critical user flows
- Security tests for authentication
- Performance tests for dashboard loading

## Maintenance Guidelines

- Regularly update dependencies
- Monitor security vulnerabilities
- Review and rotate secrets
- Monitor application performance
- Keep documentation current
- Plan for data retention policies

---

**Note:** This project emphasizes defensive security practices. All code should be reviewed for security implications, especially authentication, data handling, and API integrations.