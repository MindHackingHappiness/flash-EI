# Use an official Node.js runtime as a parent image
FROM node:18-slim

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the current directory contents into the container
COPY . .

# Create a .env file from the example if it doesn't exist
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Run example.js when the container launches
CMD ["node", "example.js"]
