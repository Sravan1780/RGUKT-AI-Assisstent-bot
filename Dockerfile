FROM python:3.11-slim

WORKDIR /app

# Copy everything
COPY . .

# Install Python dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Set working directory to backend so uvicorn can find the app module
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Start backend
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]