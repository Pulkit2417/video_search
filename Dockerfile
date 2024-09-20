# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

RUN apt update && apt install ffmpeg -y

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . /app/

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
