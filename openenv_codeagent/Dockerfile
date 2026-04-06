# OpenEnv CodeAgent Dockerfile
# Deployable to HuggingFace Spaces (SDK: docker)

FROM python:3.11-slim

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── App dir ───────────────────────────────────────────────────────────────────
WORKDIR /app

# ── Python deps ───────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project ─────────────────────────────────────────────────────────────
COPY . .

# ── HuggingFace Spaces expects port 7860 ─────────────────────────────────────
EXPOSE 7860

# ── Entrypoint ────────────────────────────────────────────────────────────────
CMD ["python", "app/main.py"]
