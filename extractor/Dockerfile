# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Copy the current directory contents into the container 
ADD . /extractor

# Set the working directory 
WORKDIR /extractor

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

#entry command
CMD ["python", "-u", "extractor.py"]