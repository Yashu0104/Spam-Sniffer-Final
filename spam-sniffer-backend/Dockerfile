# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the backend files into the container
COPY . /app

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 to the outside world
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV MONGO_URI=mongodb://mongo:27017
ENV GOOGLE_CLIENT_SECRET=your_google_client_secret_file

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
