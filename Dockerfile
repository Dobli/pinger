# Use an official Python runtime as a parent image
FROM python:3
ENV PYTHONBUFFERED 1

# Use settings file of production mode
ENV DJANGO_SETTINGS_MODULE="pinger.settings_prod"

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000
