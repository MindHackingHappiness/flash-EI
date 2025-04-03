# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -e .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable for Streamlit to run in headless mode
ENV STREAMLIT_SERVER_HEADLESS=true

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]
