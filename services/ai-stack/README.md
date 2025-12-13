# AI Services Stack

GPU-accelerated AI services for Socrates homelab, designed to run on a single Tesla P40 container.

## Services

| Service | Port | Purpose |
|---------|------|---------|
| **Ollama** | 11434 | Local LLM server (GPU accelerated) |
| **Karakeep** | 3000 | AI-powered bookmarking |
| Meilisearch | 7700 (internal) | Search backend |
| Chrome | 9222 (internal) | Browser automation |

## Quick Start

```bash
./setup.sh
```

This will:
1. Generate secure credentials in `.env`
2. Create data directories
3. Pull Docker images
4. Start all services
5. Optionally pull default Ollama models

## Manual Setup

```bash
# Generate .env with random secrets
./setup.sh --generate

# Or copy and edit manually
cp .env.example .env
# Edit .env with your values

# Start services
docker compose up -d
```

## Usage

### Ollama - Local LLMs

```bash
# List available models
docker exec ollama ollama list

# Pull a model
docker exec ollama ollama pull llama3.2:3b
docker exec ollama ollama pull llava:7b     # Vision model
docker exec ollama ollama pull codellama    # Code model

# Chat directly
docker exec -it ollama ollama run llama3.2:3b

# API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Hello!"
}'
```

### Karakeep - Bookmarking

- Web UI: http://localhost:3000
- Create account on first visit
- Install browser extension for quick saves
- AI tagging uses Ollama automatically

## Configuration

### Environment Variables

Key settings in `.env`:

```bash
# Karakeep
NEXTAUTH_URL=http://your-ip:3000  # Change for remote access

# Ollama models for Karakeep
INFERENCE_TEXT_MODEL=llama3.2:3b
INFERENCE_IMAGE_MODEL=llava:7b
```

### Cloud API Keys (Optional)

For enhanced capabilities, add API keys:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### GPU Memory

Tesla P40 has 24GB VRAM. Typical usage:
- llama3.2:3b - ~3GB
- llava:7b - ~5GB
- Larger models available with remaining VRAM

## Management

```bash
# View logs
docker compose logs -f
docker compose logs -f ollama  # Specific service

# Check status
docker compose ps

# Restart a service
docker compose restart karakeep

# Stop all
docker compose down

# Update images
docker compose pull && docker compose up -d

# Backup data
tar -czf ai-stack-backup.tar.gz data/
```

## Network Access

To access from other machines, update `.env`:

```bash
NEXTAUTH_URL=http://10.203.x.x:3000  # Karakeep
```

Then access:
- Karakeep: http://10.203.x.x:3000
- Ollama API: http://10.203.x.x:11434

## Troubleshooting

### GPU not detected
```bash
# Verify NVIDIA driver
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### Ollama out of memory
```bash
# Use smaller model
docker exec ollama ollama pull llama3.2:1b

# Or unload unused models
docker exec ollama ollama rm large-model
```

### Services won't start
```bash
# Check logs
docker compose logs

# Reset
docker compose down -v
./setup.sh
```

## Data Locations

```
./data/
└── (Docker volumes for persistent data)
```

## Adding More Services

This stack is designed to be extended. Add new AI services to `docker-compose.yml`:

```yaml
services:
  new-service:
    image: ...
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    networks:
      - ai-network
```
