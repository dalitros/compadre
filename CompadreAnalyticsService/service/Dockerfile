# Use an official Python runtime as a parent image
FROM public.ecr.aws/docker/library/python:3.11-slim-bullseye

# Set the working directory to /app
WORKDIR /

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose port 8000 for the Django app
EXPOSE 8000

# Start the Django app when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]