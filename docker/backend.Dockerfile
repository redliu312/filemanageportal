FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH and verify installation
ENV PATH="/root/.local/bin:${PATH}"
RUN uv --version

# Copy Python version and project files
COPY .python-version pyproject.toml requirements.txt ./

# Create virtual environment and install dependencies
RUN uv venv .venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Copy application code
COPY . .

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Set Flask app
ENV FLASK_APP=src.app:app

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]