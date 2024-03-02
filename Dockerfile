# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

expose 5000 

CMD ["python3", "app.py"]