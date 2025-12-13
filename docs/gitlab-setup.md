# GitLab Setup Guide

Self-hosted GitLab CE deployment on Rawls using Docker.

## Overview

GitLab provides:
- Git repository hosting
- CI/CD pipelines
- Container registry (optional)
- Issue tracking and project management

**Host**: Rawls (10.203.3.47)
**Access**: http://10.203.3.47 or http://gitlab.lab.local

## Quick Start

### Deploy GitLab

```bash
# Deploy to Rawls only
ansible-playbook -i ansible/inventory-prod.ini ansible/site.yml \
  --limit rawls \
  --tags gitlab

# Or run full playbook for Rawls
ansible-playbook -i ansible/inventory-prod.ini ansible/site.yml \
  --limit rawls
```

### First Login

1. Access GitLab at http://10.203.3.47
2. Username: `root`
3. Get initial password:
   ```bash
   ssh rawls "docker exec gitlab cat /etc/gitlab/initial_root_password"
   ```
4. **Change the password immediately** - it expires in 24 hours

## Architecture

```
Rawls (10.203.3.47)
├── Docker
│   └── gitlab-stack/
│       ├── gitlab (CE)
│       └── gitlab-runner (optional)
└── /opt/gitlab-stack/
    ├── docker-compose.yml
    └── .env
```

### Ports

| Service | Port | Description |
|---------|------|-------------|
| HTTP | 80 | Web interface |
| HTTPS | 443 | Secure web (if configured) |
| SSH | 2222 | Git over SSH |

## Configuration

### Host Variables

Edit `ansible/host_vars/rawls.yml`:

```yaml
# Enable GitLab
gitlab_deploy: true

# Access URL
gitlab_external_url: "http://10.203.3.47"

# SSH port (non-standard to avoid conflict)
gitlab_ssh_port: 2222

# Enable CI/CD runner
gitlab_deploy_runner: false  # Enable after setup
```

### Memory Requirements

GitLab is memory-intensive:
- Minimum: 4GB RAM
- Recommended: 8GB+ RAM

The role disables Prometheus and Grafana monitoring to reduce memory usage.

## Usage

### Clone a Repository

```bash
# Via SSH (recommended)
git clone ssh://git@10.203.3.47:2222/group/project.git

# Via HTTP
git clone http://10.203.3.47/group/project.git
```

### Mirror from GitHub

1. Create a new project in GitLab
2. Go to Settings > Repository > Mirroring repositories
3. Add GitHub URL: `https://github.com/username/repo.git`
4. Select "Pull" direction
5. Authenticate if private

### Set Up CI/CD Runner

After GitLab is running:

1. Enable the runner in `host_vars/rawls.yml`:
   ```yaml
   gitlab_deploy_runner: true
   ```

2. Re-run the playbook:
   ```bash
   ansible-playbook -i ansible/inventory-prod.ini ansible/site.yml \
     --limit rawls --tags gitlab
   ```

3. Register the runner:
   ```bash
   ssh rawls "docker exec -it gitlab-runner gitlab-runner register"
   ```

## Operations

### View Logs

```bash
ssh rawls "docker logs gitlab"
ssh rawls "docker logs -f gitlab"  # Follow
```

### Check Status

```bash
ssh rawls "docker exec gitlab gitlab-ctl status"
```

### Restart Services

```bash
ssh rawls "docker compose -f /opt/gitlab-stack/docker-compose.yml restart"
```

### Reconfigure

```bash
ssh rawls "docker exec gitlab gitlab-ctl reconfigure"
```

### Backup

GitLab includes automatic backups. To trigger manually:

```bash
ssh rawls "docker exec gitlab gitlab-backup create"
```

Backups are stored in the `gitlab_data` volume at `/var/opt/gitlab/backups/`.

### Restore

```bash
# Stop services
ssh rawls "docker exec gitlab gitlab-ctl stop puma"
ssh rawls "docker exec gitlab gitlab-ctl stop sidekiq"

# Restore (replace TIMESTAMP with actual backup file)
ssh rawls "docker exec gitlab gitlab-backup restore BACKUP=TIMESTAMP"

# Restart
ssh rawls "docker compose -f /opt/gitlab-stack/docker-compose.yml restart"
```

## Troubleshooting

### GitLab Won't Start

Check if ports are in use:
```bash
ssh rawls "ss -tlnp | grep -E ':(80|443|2222)'"
```

### Out of Memory

GitLab needs significant RAM. Check memory usage:
```bash
ssh rawls "free -h"
ssh rawls "docker stats gitlab --no-stream"
```

### Health Check Failing

```bash
ssh rawls "docker exec gitlab gitlab-rake gitlab:check SANITIZE=true"
```

### View All GitLab Logs

```bash
ssh rawls "docker exec gitlab gitlab-ctl tail"
```

## Integration with This Homelab

### Recommended Repositories to Mirror

1. `homelab-automation` - This repository
2. `dotfiles` - Personal dotfiles
3. `descartes-stack` - Legacy configuration (reference)

### CI/CD Pipeline Ideas

1. **Ansible Lint**: Validate playbooks on push
2. **Terraform Plan**: Preview infrastructure changes
3. **Docker Build**: Build and push container images

## Files Created

| Path | Description |
|------|-------------|
| `ansible/roles/gitlab/` | Ansible role |
| `ansible/host_vars/rawls.yml` | Rawls configuration |
| `services/gitlab-stack/` | Docker compose reference |
| `docs/gitlab-setup.md` | This documentation |

## Next Steps

1. [ ] Change root password
2. [ ] Create personal admin account
3. [ ] Mirror GitHub repositories
4. [ ] Set up SSH key authentication
5. [ ] Configure CI/CD runner
6. [ ] Set up backup schedule
