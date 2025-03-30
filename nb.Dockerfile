FROM jupyter/base-notebook:latest

# Use root user for installing system-level dependencies
USER root

# Install Node.js, npm, and Playwright system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm && \
    npx playwright install-deps && \
    rm -rf /var/lib/apt/lists/*

# Switch back to default user
USER jovyan

COPY nb/dependencies.txt /home/jovyan/work/dependencies.txt

RUN pip install --no-cache-dir -r /home/jovyan/work/dependencies.txt && playwright install