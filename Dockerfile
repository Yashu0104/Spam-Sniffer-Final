# Use official Node.js image as a parent image
FROM node:18-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the frontend package files and install dependencies
COPY ./frontend/package*.json /app/
RUN npm install

# Copy the entire frontend project files
COPY ./frontend /app/

# Expose the React app's port
EXPOSE 3000

# Run the React app
CMD ["npm", "start"]
