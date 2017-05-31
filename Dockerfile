

# Use an official Python runtime as a base image
FROM python:3.5

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container
ADD . /app

# Open port 80 for https access
EXPOSE 5000

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Export token to working environment and start app
CMD ["bash", "export ara_location=$(python -c "import os,ara; print(os.path.dirname(ara.__file__))")"]
CMD ["bash", "export ANSIBLE_CALLBACK_PLUGINS=$ara_location/plugins/callbacks"]
CMD ["bash", "export ANSIBLE_ACTION_PLUGINS=$ara_location/plugins/actions"]
CMD ["bash", "export ANSIBLE_LIBRARY=$ara_location/plugins/modules"]

CMD ["python", "./bin/slacksible.py"]
