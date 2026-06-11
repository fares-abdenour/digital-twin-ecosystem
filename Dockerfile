# 1. Use an official lightweight Python runtime base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file first to leverage Docker caching layers
COPY requirements.txt .

# 4. Install the production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the source code directory into the container
COPY src/ ./src/

# 6. Expose the execution port inside the container network
EXPOSE 8000

# 7. Run the Uvicorn production server on container startup
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]