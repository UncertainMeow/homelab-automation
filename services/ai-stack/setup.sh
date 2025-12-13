#!/bin/bash
# AI Apps Stack Setup - Karakeep
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

generate_secret() {
    openssl rand -base64 32 | tr -d '/+=' | head -c 32
}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  AI Apps Stack Setup - Karakeep"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check for OLLAMA_HOST
if [ -z "$OLLAMA_HOST" ] && [ ! -f .env ]; then
    echo "OLLAMA_HOST is required (IP of ai-gpu0 container)"
    read -p "Enter ai-gpu0 IP address: " OLLAMA_HOST
    if [ -z "$OLLAMA_HOST" ]; then
        log_error "OLLAMA_HOST is required"
        exit 1
    fi
fi

# Generate .env
if [ ! -f .env ]; then
    log_info "Generating .env with secure secrets..."
    cat > .env << EOF
# AI Apps Stack Configuration
# Generated: $(date -Iseconds)

# Ollama Host (ai-gpu0)
OLLAMA_HOST=${OLLAMA_HOST}

# Karakeep
KARAKEEP_VERSION=release
KARAKEEP_PORT=3000
NEXTAUTH_SECRET=$(generate_secret)
NEXTAUTH_URL=http://localhost:3000
MEILISEARCH_MASTER_KEY=$(generate_secret)

# Ollama Models
INFERENCE_TEXT_MODEL=llama3.2:3b
INFERENCE_IMAGE_MODEL=llava:7b
INFERENCE_CONTEXT_LENGTH=2048

# Optional: Cloud API Fallback
# OPENAI_API_KEY=
EOF
    log_ok ".env created"
else
    log_info ".env already exists"
    # Source existing to get OLLAMA_HOST
    source .env
fi

# Test Ollama connectivity
log_info "Testing Ollama connectivity at ${OLLAMA_HOST}:11434..."
if curl -sf "http://${OLLAMA_HOST}:11434/api/tags" > /dev/null 2>&1; then
    log_ok "Ollama reachable"
else
    log_warn "Cannot reach Ollama at ${OLLAMA_HOST}:11434"
    log_warn "Make sure LLM stack is running on ai-gpu0"
fi

# Pull and start
log_info "Pulling images..."
docker compose pull

log_info "Starting services..."
docker compose up -d

# Wait for Karakeep
log_info "Waiting for Karakeep to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        log_ok "Karakeep ready"
        break
    fi
    sleep 2
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  AI Apps Stack Ready!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Services:"
echo "  Karakeep:  http://localhost:3000"
echo ""
echo "Using Ollama at: http://${OLLAMA_HOST}:11434"
echo ""
echo "First visit Karakeep to create your account."
echo "Install browser extension for quick bookmarking."
echo ""
