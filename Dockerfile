FROM python:3.11-slim

WORKDIR /app

# Install Node.js for frontend (if needed for static build)
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Copy everything
COPY . .

# Install Python dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start backend
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]