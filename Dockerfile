# Use an official lightweight Python image.
FROM python:3.11.9-slim

# Set working directory in the container.
WORKDIR /app

# Add Debian security repository
RUN echo "deb http://security.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file to install dependencies.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy the rest of the application code.
COPY . .

EXPOSE 8001

# Command to run the server.
CMD ["python", "app.py"]
