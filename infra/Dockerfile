
# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy source code
COPY ../src /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn scrapy typer parsel pydantic python-multipart ruff black mypy pytest requests-mock pytest-cov playwright
RUN playwright install --with-deps

# Expose ports
EXPOSE 8000 3000

# Command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
