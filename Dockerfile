# Use an official lightweight Python image.
FROM python:3.11.9-slim

# Set working directory in the container.
WORKDIR /app

# Add Debian security repository
RUN apt-get update && apt-get install -y

# Copy the requirements file to install dependencies.
COPY requirements.txt .

# Install Python dependencies.
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

EXPOSE 8000

# Command to run the server.
CMD ["python", "server.py"]
