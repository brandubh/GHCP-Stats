# Configuration

## Environment Variables

GHCP-Stats uses environment variables for configuration settings. These should be set in the deployment environment or in a `.env` file during development.

### Core Configuration

```
# Server Configuration
PORT=3000
NODE_ENV=production
LOG_LEVEL=info

# Database Configuration
DB_NAME=your_database_name
PERSISTENT_STORAGE=mounted volume
AZURE_KEY_VAULT_URI=https://your-key-vault-name.vault.azure.net/

# GitHub Integration
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Authentication
JWT_SECRET=your_jwt_secret
JWT_EXPIRATION=24h
COOKIE_SECRET=your_cookie_secret

# Feature Flags
ENABLE_REAL_TIME_ANALYTICS=true
ENABLE_TEAM_COMPARISONS=true
ENABLE_PREDICTIVE_MODELS=false
```

### Advanced Configuration

```
# Performance Tuning
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT_MS=30000
WORKER_THREADS=4

# Data Collection
COLLECTION_BATCH_SIZE=50
COLLECTION_INTERVAL_MS=5000
MAX_EVENT_AGE_DAYS=90

# Caching
CACHE_TTL_SECONDS=300
DASHBOARD_CACHE_TTL_SECONDS=60

# Rate Limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100

# Security
CORS_ALLOWED_ORIGINS=https://example.com,https://admin.example.com
TLS_CERT_PATH=/path/to/cert.pem
TLS_KEY_PATH=/path/to/key.pem
```

## Configuration Files

In addition to environment variables, the system uses configuration files for more complex settings.

### `config/data-collection.json`

This file controls what data is collected and how it's processed:

```json
{
  "eventTypes": {
    "suggestion": {
      "enabled": true,
      "sampleRate": 1.0,
      "privacyFilters": ["removeCodeSnippets", "anonymizeIdentifiers"]
    },
    "acceptance": {
      "enabled": true,
      "sampleRate": 1.0,
      "privacyFilters": []
    },
    "rejection": {
      "enabled": true,
      "sampleRate": 0.5,
      "privacyFilters": []
    },
    "modification": {
      "enabled": true,
      "sampleRate": 0.25,
      "privacyFilters": ["removeCodeSnippets"]
    }
  },
  "contextData": {
    "collectLanguage": true,
    "collectFileType": true,
    "collectRepositoryName": true,
    "collectBranchName": false,
    "collectDirectoryStructure": false,
    "tokenCounting": true
  },
  "retention": {
    "rawEventRetentionDays": 30,
    "aggregatedDataRetentionDays": 365,
    "archiveExpiredData": true,
    "archiveFormat": "parquet"
  }
}
```

### `config/metrics.json`

This file defines the metrics calculated by the system:

```json
{
  "standardMetrics": {
    "acceptanceRate": {
      "enabled": true,
      "description": "Percentage of suggestions accepted",
      "formula": "acceptedSuggestions / totalSuggestions",
      "aggregations": ["daily", "weekly", "monthly"],
      "dimensions": ["language", "fileType", "projectType"]
    },
    "modificationRate": {
      "enabled": true,
      "description": "Average percentage of accepted suggestions that were modified",
      "formula": "sum(modificationPercentage) / acceptedSuggestions",
      "aggregations": ["daily", "weekly", "monthly"],
      "dimensions": ["language", "fileType"]
    },
    "timeSaved": {
      "enabled": true,
      "description": "Estimated time saved based on suggestion length and acceptance",
      "formula": "acceptedSuggestions * averageTokensPerSuggestion * timePerTokenFactor",
      "aggregations": ["daily", "weekly", "monthly"],
      "dimensions": ["user", "team", "project"]
    }
  },
  "customMetrics": {
    "complexitySavings": {
      "enabled": false,
      "description": "Estimation of complexity avoided through Copilot suggestions",
      "formula": "custom",
      "implementation": "metrics/complexity.js",
      "aggregations": ["weekly", "monthly"],
      "dimensions": ["language"]
    }
  },
  "benchmarks": {
    "industry": {
      "acceptanceRate": 0.65,
      "modificationRate": 0.45,
      "timeSavedPerDay": 25
    }
  }
}
```

### `config/dashboard.json`

This file configures the dashboard layouts and visualizations:

```json
{
  "defaultDashboard": {
    "layout": "grid",
    "refreshInterval": 300,
    "widgets": [
      {
        "id": "acceptance-rate-trend",
        "type": "lineChart",
        "title": "Acceptance Rate Trend",
        "metric": "acceptanceRate",
        "period": "last30Days",
        "dimensions": ["daily"],
        "position": {"row": 0, "col": 0, "width": 6, "height": 4}
      },
      {
        "id": "language-breakdown",
        "type": "pieChart",
        "title": "Suggestions by Language",
        "metric": "suggestionsReceived",
        "period": "last30Days",
        "dimensions": ["language"],
        "position": {"row": 0, "col": 6, "width": 6, "height": 4}
      },
      {
        "id": "time-saved-kpi",
        "type": "kpiCard",
        "title": "Estimated Time Saved",
        "metric": "timeSaved",
        "period": "last30Days",
        "format": "hours",
        "comparison": "previousPeriod",
        "position": {"row": 4, "col": 0, "width": 4, "height": 3}
      }
    ]
  },
  "userDashboard": {
    "layout": "flex",
    "refreshInterval": 600,
    "widgets": [
      // User-specific widgets configuration
    ]
  },
  "teamDashboard": {
    "layout": "grid",
    "refreshInterval": 900,
    "widgets": [
      // Team-specific widgets configuration
    ]
  }
}
```

## Deployment Parameters

When deploying GHCP-Stats, the following parameters should be configured based on the target environment:

### Production Deployment

- **Scaling Parameters**:
  - Minimum of 3 application instances for high availability
  - Auto-scaling based on CPU utilization (target: 70%)
  - Database connection pool size: 20-50 connections

- **Resource Requirements**:
  - Application: 2 CPU cores, 4GB RAM per instance
  - Database: 4 CPU cores, 16GB RAM, 100GB storage
  - Cache: 2 CPU cores, 8GB RAM

- **Network Configuration**:
  - Internal service mesh for component communication
  - SSL termination at load balancer
  - Rate limiting at API gateway (200 req/min per user)

- **Backup Strategy**:
  - Database: Daily full backups, hourly incremental backups
  - Configuration: Version-controlled and backed up with each deployment
  - Retention: 30 days of rolling backups

### Development Deployment

- **Scaling Parameters**:
  - Single application instance
  - Database connection pool size: 5-10 connections

- **Resource Requirements**:
  - Application: 1 CPU core, 2GB RAM
  - Database: 2 CPU cores, 4GB RAM, 20GB storage
  - Cache: 1 CPU core, 2GB RAM

- **Network Configuration**:
  - Local development network
  - Self-signed SSL certificates
  - No rate limiting

- **Backup Strategy**:
  - Database: Daily full backups
  - Configuration: Local version control
  - Retention: 7 days of rolling backups
