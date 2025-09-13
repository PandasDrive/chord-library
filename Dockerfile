# Use an official, lightweight Python version as the base
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python libraries listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all of your project files (app.py, index.html, etc.) into the container
COPY . .

# The command to run when the container starts.
# This tells Gunicorn to serve your app.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]