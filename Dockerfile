FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/?wsdl')"

# Wait for database and start application
CMD ["sh", "-c", "python -c \"\
import time, psycopg2, os\n\
db_host = os.getenv('DB_HOST', 'postgres')\n\
db_port = os.getenv('DB_PORT', '5432')\n\
db_name = os.getenv('DB_NAME', 'wallet_db')\n\
db_user = os.getenv('DB_USER', 'postgres')\n\
db_password = os.getenv('DB_PASSWORD', 'postgres')\n\
max_retries = 30\n\
for i in range(max_retries):\n\
    try:\n\
        conn = psycopg2.connect(\n\
            host=db_host,\n\
            port=db_port,\n\
            database=db_name,\n\
            user=db_user,\n\
            password=db_password\n\
        )\n\
        conn.close()\n\
        print('Database connection successful')\n\
        break\n\
    except Exception as e:\n\
        if i == max_retries - 1:\n\
            raise e\n\
        print('Waiting for database... (attempt {}/{})'.format(i+1, max_retries))\n\
        time.sleep(2)\n\
\" && python app.py"]
