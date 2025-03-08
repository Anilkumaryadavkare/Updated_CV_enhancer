# Use Python 3.9 as the base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy all the files from your repo to the container
COPY . .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy model during build
RUN python -m spacy download en_core_web_sm

# Expose port 8000 for the application
EXPOSE 8000

# Run the application using app.py (modify if needed)
CMD ["python", "app.py"]
