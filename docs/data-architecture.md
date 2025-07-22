# Data Architecture

Metrics are stored in a single SQLite database table called `metrics`.

```sql
CREATE TABLE metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  org TEXT,
  date TEXT,
  data TEXT
);
```

The `data` column contains the JSON object returned by the GitHub API for a given day and organisation. Helper functions parse this JSON when building the data frames used by the dashboard.

No additional tables or relations are defined. When running in a container the database file can be mounted on a persistent volume.
