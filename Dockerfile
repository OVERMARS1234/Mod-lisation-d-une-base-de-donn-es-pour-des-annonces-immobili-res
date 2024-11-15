# Use an official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

COPY . /app
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
CMD ["python", "brif_3.py"] 

