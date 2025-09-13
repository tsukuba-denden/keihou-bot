# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv pip sync --no-cache

# Copy the source code
COPY src/ ./src

# Set environment variables for Discord and JMA (placeholders)
# These should be passed in at runtime (e.g., with `docker run -e ...`)
ENV DISCORD_WEBHOOK_URL=""
ENV JMA_FEED_URL="https://www.data.jma.go.jp/developer/xml/feed/extra.xml"
ENV FETCH_INTERVAL_MIN="5"

# Command to run the application
CMD ["python", "-m", "src.main"]
