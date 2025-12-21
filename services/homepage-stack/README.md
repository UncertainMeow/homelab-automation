# Homepage Dashboard

A modern, fully static, fast dashboard for the homelab.

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Get API tokens:**

   **Proxmox API Token:**
   - Datacenter → Permissions → API Tokens → Add
   - User: `root@pam` (or create dedicated user)
   - Token ID: `homepage`
   - Copy the token value

   **UniFi API Key:**
   - Already configured: `KdUEfY_59qUUkMjPyZsJtIpNIeYVfjhA`

   **Technitium DNS Token:**
   - Login to http://10.203.3.203:5380
   - Use the API login endpoint to get a session token

3. **Deploy:**
   ```bash
   docker-compose up -d
   ```

4. **Access:**
   - http://localhost:3000 (or container IP)

## Configuration Files

| File | Purpose |
|------|---------|
| `config/settings.yaml` | Theme, layout, background |
| `config/services.yaml` | Service cards and widgets |
| `config/widgets.yaml` | Top bar widgets |
| `config/bookmarks.yaml` | Quick links |
| `config/docker.yaml` | Docker integration |

## Services Configured

### Infrastructure
- Proxmox (Socrates, Rawls, Zeno)
- PBS (Plato)

### AI Services
- Ollama API
- Open WebUI
- Karakeep

### Network
- UniFi Controller
- Technitium DNS
- Tailscale

### Management
- GitLab
- Netbox
- Dockge

## Customization

Edit the YAML files in `config/` to customize. Homepage auto-reloads on config changes.

### Adding Services

```yaml
- Category Name:
    - Service Name:
        icon: icon-name.png
        href: http://service-url
        description: Service description
        widget:
          type: widget-type
          # widget-specific options
```

### Icons

Browse available icons: https://github.com/walkxcode/dashboard-icons

## Documentation

- https://gethomepage.dev/
- https://gethomepage.dev/configs/services/
- https://gethomepage.dev/widgets/
