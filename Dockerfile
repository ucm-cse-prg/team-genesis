# Set the base image for the build stage
FROM python:3.13-slim-bookworm

# Install the latest version of uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app

# Copy the project into the image
ADD . /app

# Install the project
RUN uv sync --frozen

# Build the project
RUN uv build

# Set the base image for the project
FROM python:3.13-slim-bookworm

# Set the project directory inside the image
WORKDIR /app

# Copy the built project package into the image
COPY --from=0 /app/dist/*.tar.gz .

# Extract the built project package
RUN tar -xf *.tar.gz --strip-components=1

# Install the project package
RUN pip install .

# Run the project
CMD ["fastapi-app", "--host", "0.0.0.0", "--port", "8000"]