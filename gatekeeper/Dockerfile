# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Copy the current directory contents into the container 
ADD . /gatekeeper

# Set the working directory
WORKDIR /gatekeeper

# Environment variables for database
ENV DBHOST mongo

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Set up flask app
ENV FLASK_APP gatekeeper
RUN pip install -e .

# Make port 80 available to the world outside this container
EXPOSE 80

#entry command
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "80"]
