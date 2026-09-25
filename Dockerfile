FROM python:3.11-slim

WORKDIR /app

# System deps for snowflake-connector-python's pandas extra (pyarrow wheels
# are prebuilt for slim images, but a couple of build tools smooth over
# platform edge cases) and general SSL/cert handling.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py db.py ./

# Snowpark Container Services routes traffic to whatever port the service
# spec declares; 8000 is Shiny's default and what the spec (service_spec.yaml)
# below expects.
EXPOSE 8000

# Credentials arrive as env vars injected by the Snowpark service spec
# (via SNOWFLAKE_PASSWORD etc. referenced from Snowflake secrets) — db.py
# reads them the same way it does locally via python-dotenv, so no code
# changes were needed between Phase 2 and Phase 3.
CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
