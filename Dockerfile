# Use an official, lightweight Python version as the base
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly copy the application and the templates folder
COPY app.py .
COPY templates ./templates/

# --- MODIFIED: Added --chdir flag to the CMD instruction ---
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--chdir", "/app", "app:app"]