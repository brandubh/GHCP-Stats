FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Expose Streamlit port
EXPOSE 8501
# Create volume mount point for SQLite database
VOLUME /app/data

CMD ["streamlit", "run", "src/app.py"]