FROM python:3.11

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /usr/src/app

# Install netcat for MySQL connection check
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make entrypoint script executable
RUN chmod +x scripts/entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["./scripts/entrypoint.sh"]

# gunicorn
CMD ["gunicorn", "--config", "docker/gunicorn-cfg.py", "core.wsgi"]
