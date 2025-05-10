# Use the official Python image from the Docker hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the poetry files to install dependencies
COPY pyproject.toml poetry.lock* ./

# Install poetry and dependencies
RUN pip install "poetry==1.8.2" && poetry install --no-interaction --no-ansi

# Copy the backend code into the container
COPY backend ./backend

# Expose the port the app will run on
EXPOSE 8000

# Run the application with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
