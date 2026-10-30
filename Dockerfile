FROM node:22-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN npm --prefix frontend ci --no-audit --no-fund
COPY frontend ./frontend
RUN npm --prefix frontend run build

FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY routewise routewise
COPY backend backend
COPY models.yaml .
COPY --from=frontend-build /build/frontend/dist frontend/dist
RUN pip install --no-cache-dir .
ENV PORT=3000
EXPOSE 3000
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-3000}"]
