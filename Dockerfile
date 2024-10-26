# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /web

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the application code
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Command to run the application
ENTRYPOINT ["streamlit", "run"]
CMD ["web.py", "--server.port=8501", "--server.address=0.0.0.0"]
