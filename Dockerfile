FROM oven/bun:1.3.14-debian

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .
RUN cd wordseek && bun install --frozen-lockfile

ENV PATH="/opt/venv/bin:$PATH"
CMD ["bash", "./start-all.sh"]
