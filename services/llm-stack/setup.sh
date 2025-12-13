#!/bin/bash
# LLM Stack Setup - Ollama + Open WebUI + Khoj
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

generate_secret() {
    openssl rand -base64 32 | tr -d '/+=' | head -c 32
}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  LLM Stack Setup - Ollama + Open WebUI + Khoj"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Generate .env
if [ ! -f .env ]; then
    log_info "Generating .env with secure secrets..."
    cat > .env << EOF
# LLM Stack Configuration
# Generated: $(date -Iseconds)

TIMEZONE=America/New_York

# Open WebUI
WEBUI_PORT=8080
WEBUI_SECRET_KEY=$(generate_secret)
WEBUI_AUTH=true

# Khoj
KHOJ_PORT=42110
KHOJ_ADMIN_EMAIL=admin@localhost
KHOJ_ADMIN_PASSWORD=$(generate_secret)
KHOJ_DJANGO_SECRET_KEY=$(generate_secret)

# Optional: Cloud API Keys
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=
EOF
    log_ok ".env created"
else
    log_info ".env already exists, keeping existing"
fi

# Create data directories
log_info "Creating data directories..."
mkdir -p data/khoj/documents data/khoj/inbox
log_ok "Directories created"

# Check GPU
log_info "Checking GPU..."
if nvidia-smi &>/dev/null; then
    nvidia-smi -L
    log_ok "GPU detected"
else
    log_warn "No GPU detected - Ollama will run on CPU"
fi

# Pull and start
log_info "Pulling images (this may take a while)..."
docker compose pull

log_info "Starting services..."
docker compose up -d

# Wait for Ollama
log_info "Waiting for Ollama to be ready..."
for i in {1..60}; do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_ok "Ollama ready"
        break
    fi
    sleep 2
done

# Pull starter models
echo ""
log_info "Pulling starter models..."
log_info "  llama3.2:3b (fast, good for chat)..."
docker exec ollama ollama pull llama3.2:3b 2>/dev/null || log_warn "Failed to pull llama3.2:3b"

log_info "  nomic-embed-text (for Khoj embeddings)..."
docker exec ollama ollama pull nomic-embed-text 2>/dev/null || log_warn "Failed to pull nomic-embed-text"

# Get container IP for cross-container access
CONTAINER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  LLM Stack Ready!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Services (local):"
echo "  Ollama API:    http://localhost:11434"
echo "  Open WebUI:    http://localhost:8080"
echo "  Khoj:          http://localhost:42110"
echo ""
echo "Services (from other containers):"
echo "  Ollama API:    http://${CONTAINER_IP}:11434"
echo ""
echo "Khoj Credentials:"
grep -E "^KHOJ_ADMIN" .env | sed 's/^/  /'
echo ""
echo "Pull more models:"
echo "  docker exec ollama ollama pull mistral"
echo "  docker exec ollama ollama pull llama3.1:70b"
echo "  docker exec ollama ollama pull llava:7b"
echo ""
