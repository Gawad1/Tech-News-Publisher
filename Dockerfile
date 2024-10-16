# Use official Python slim image
FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Set ENTRYPOINT to run your script
ENTRYPOINT ["./start.sh"]

# Expose the port on which Flask will run
EXPOSE 5000
