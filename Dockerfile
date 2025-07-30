FROM python:3.11.3-bullseye

# Install system dependencies and upgrade pip
RUN apt update -y && apt install -y \
    build-essential \
    python3-pip \
 && pip3 install --upgrade pip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

EXPOSE 5000

ARG DB_NAME

ENV ENV_NAME=staging \
    ALLOWED_HOSTS=* \
    DB_NAME=${DB_NAME}

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create .env from template
RUN mv .env.example .env

# Start Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]
