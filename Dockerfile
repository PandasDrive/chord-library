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

# --- NEW: Add this command to see all files in the build log ---
RUN ls -R

# The command to run when the container starts.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]