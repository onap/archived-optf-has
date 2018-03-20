# Use an official Python runtime as a parent image
FROM python:2.7

# Set the working directory to /su/python/webpy-rest-dockerized
WORKDIR /opt/aaisim

# Copy the current directory contents into the container at /app
ADD ./  /opt/aaisim

# Install any needed packages specified in requirements.txt
RUN pip install web.py

# Make port 80 available to the world outside this container
EXPOSE 8081

# Define environment variable
ENV NAME aaisim

# Run aaisim.py when the container launches
CMD ["/bin/sh", "-c", "python -u aaisim.py 8081 > /tmp/aaisim.log 2>&1"]

