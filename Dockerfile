# Use the official lightweight Python 3.8.19-bullseye image
FROM python:3.8.19-bullseye

# Set the working directory
WORKDIR /main

# Install CMake and other dependencies
RUN apt-get update && apt-get install -y cmake 
RUN apt-get update && apt install -y libgl1-mesa-glx
RUN python -m venv ocr

ENV PATH="/main/ocr/bin:$PATH"

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port the app runs on
EXPOSE 3050

# Run the application
CMD ["python3", "main.py"]