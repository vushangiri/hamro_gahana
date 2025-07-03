# Use official Python base image
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose Flask port
EXPOSE 5000

# Command to run app
CMD ["python", "run.py"]
