# Stage 1: build frontend
FROM node:18 AS frontend-build
WORKDIR /usr/src/app/frontend
COPY frontend/package.json frontend/tsconfig.json frontend/vite.config.ts ./
COPY frontend/src ./src
COPY frontend/index.html ./
RUN npm install && npm run build

# Stage 2: build backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY --from=frontend-build /usr/src/app/frontend/dist ./frontend/dist
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
