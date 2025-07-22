# Solution Overview

The application is intentionally small. A background job fetches Copilot metrics from the GitHub REST API and stores them in a SQLite database. A Streamlit UI reads that database to display charts and to browse the raw data.

There are two pages exposed through Streamlit:

1. **Metrics dashboard** – charts summarising active users and code completion statistics.
2. **Database browser** – an AgGrid table that allows inspection of the stored JSON records.

Metrics can be imported on demand or scheduled once per day. When running in Azure, the import routine copies the database file to a mounted Azure File Share before and after the update.
