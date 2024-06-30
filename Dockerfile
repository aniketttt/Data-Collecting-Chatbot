FROM python:3.9-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory 
WORKDIR /usr/src/app

# Install system dependencies
RUN apk update \
    && apk add --virtual .build-deps gcc musl-dev \
    && apk add postgresql-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose port 5000 to the outside access
EXPOSE 5000

# run the application
CMD ["python", "./app.py"]
