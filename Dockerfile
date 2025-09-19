FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*


# Copy requirements for all apps
COPY Contributors-Point/requirements.txt /app/Contributors-Point/requirements.txt
COPY Projects-Guide/requirements.txt /app/Projects-Guide/requirements.txt
COPY "Auto-Thank Contributors/requirements.txt" /app/Auto-Thank-Contributors/
COPY "GitHub Tags Generator/requirements.txt" /app/GitHub-Tags-Generator/

# Install dependencies for all apps
RUN pip install --upgrade pip \
    && pip install -r /app/Contributors-Point/requirements.txt \
    && pip install -r /app/Projects-Guide/requirements.txt \
    && pip install -r /app/Auto-Thank-Contributors/requirements.txt \
    && pip install -r /app/GitHub-Tags-Generator/requirements.txt

# Copy all source code
COPY Contributors-Point /app/Contributors-Point
COPY Projects-Guide /app/Projects-Guide
COPY "Auto-Thank Contributors" /app/Auto-Thank-Contributors/
COPY "GitHub Tags Generator" /app/GitHub-Tags-Generator/
COPY "Task Scheduler" /app/Task-Scheduler/

CMD ["python", "--version"]
