# Use an official Python runtime as a base image
FROM python:3.5

# Set the working directory to /app
WORKDIR /slacksible

# Copy the current directory contents into the container
ADD . /slacksible

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run app.py when the container launches
CMD ["python", "./bin/slacksible.py -t xoxb-168959872961-Clds2jLyYvCQY3syhyEUSjKs"]
