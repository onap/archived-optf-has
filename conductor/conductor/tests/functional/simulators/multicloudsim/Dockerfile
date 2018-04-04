# Use an official Python runtime as a parent image
FROM python:2.7

# Set the working directory to /su/python/webpy-rest-dockerized
WORKDIR /opt/multicloudsim

# Copy the current directory contents into the container at /app
ADD ./  /opt/multicloudsim

# Install any needed packages specified in requirements.txt
RUN pip install web.py

# Make port 80 available to the world outside this container
EXPOSE 8082

# Define environment variable
ENV NAME multicloudsim

# Run multicloudsim.py when the container launches
CMD ["/bin/sh", "-c", "python -u multicloudsim.py 8082 > /tmp/multicloudsim.log 2>&1"]

