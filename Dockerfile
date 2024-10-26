# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install spaCy and download the model
RUN pip3 install spacy && python -m spacy download en_core_web_sm

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Set environment variables
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Create a non-root user
RUN useradd -m streamlit
RUN chown -R streamlit:streamlit /app
USER streamlit

# Command to run the application
ENTRYPOINT ["streamlit", "run"]
CMD ["scraper.py", "--server.port=8501", "--server.address=0.0.0.0"]
