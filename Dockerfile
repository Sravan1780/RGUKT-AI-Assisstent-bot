FROM python:3.11-slim

WORKDIR /app

# Copy everything
COPY . .

# Install Python dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Set working directory to backend so uvicorn can find the app module
WORKDIR /app/backend

# Build the vector database from PDF datasets
RUN python rebuild_db.py

# Start backend using Railway's PORT variable
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}