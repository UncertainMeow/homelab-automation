# GitLab Setup Guide

Self-hosted GitLab CE deployment on Rawls using LXC container with GitLab Omnibus.

## Overview

GitLab provides:
- Git repository hosting
- CI/CD pipelines
- Container registry (optional)
- Issue tracking and project management

**Proxmox Host**: Rawls (10.203.3.47)
**GitLab Container**: VMID 204 (10.203.3.204)
**Access**: http://10.203.3.204

## Architecture

```
Rawls (10.203.3.47) - Proxmox Host
└── LXC Container (VMID 204)
    ├── IP: 10.203.3.204
    ├── Debian 12
    └── GitLab Omnibus
        ├── GitLab Rails
        ├── PostgreSQL
        ├── Redis
        ├── Nginx
        └── Sidekiq
```

This approach provides:
- Isolation from the Proxmox host
- Easy backup/snapshot via Proxmox
- Simple operations with `gitlab-ctl`
- No Docker overhead

## Quick Start

### Deploy GitLab

```bash
# Deploy to Rawls (creates LXC + installs GitLab)
ansible-playbook -i ansible/inventory-prod.ini ansible/site.yml \
  --limit rawls \
  --tags gitlab
```

**Note**: First deployment takes 10-15 minutes (GitLab Omnibus installation).

### First Login

1. Access GitLab at http://10.203.3.204
2. Username: `root`
3. Get initial password:
   ```bash
   # From your workstation
   ssh rawls "pct exec 204 -- cat /etc/gitlab/initial_root_password"
   ```
4. **Change the password immediately** - it expires in 24 hours

## Configuration

### Host Variables

Edit `ansible/host_vars/rawls.yml`:

```yaml
# Enable GitLab
gitlab_deploy: true

# LXC Container settings
gitlab_vmid: 204
gitlab_hostname: "gitlab"
gitlab_container_ip: "10.203.3.204"

# Resources
gitlab_cores: 4
gitlab_memory: 8192      # 8GB - GitLab minimum is 4GB
gitlab_disk: "50G"

# Access URL
gitlab_external_url: "http://10.203.3.204"
```

### Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 20 GB | 50+ GB |

The role disables Prometheus and Grafana monitoring to reduce memory usage by ~1GB.

## Usage

### Clone a Repository

```bash
# Via SSH (recommended)
git clone git@10.203.3.204:group/project.git

# Via HTTP
git clone http://10.203.3.204/group/project.git
```

### Mirror from GitHub

1. Create a new project in GitLab
2. Go to Settings > Repository > Mirroring repositories
3. Add GitHub URL: `https://github.com/username/repo.git`
4. Select "Pull" direction
5. Authenticate if private

## Operations

### Container Management

```bash
# Enter container shell
ssh rawls "pct enter 204"

# Or execute commands directly
ssh rawls "pct exec 204 -- gitlab-ctl status"
```

### GitLab Service Commands

From inside the container (or via `pct exec`):

```bash
# Check all service status
gitlab-ctl status

# View logs (all services)
gitlab-ctl tail

# View specific service logs
gitlab-ctl tail nginx
gitlab-ctl tail postgresql

# Restart all services
gitlab-ctl restart

# Restart specific service
gitlab-ctl restart nginx

# Apply configuration changes
gitlab-ctl reconfigure
```

### Backup

```bash
# Create backup
ssh rawls "pct exec 204 -- gitlab-backup create"

# Backups stored at: /var/opt/gitlab/backups/

# List backups
ssh rawls "pct exec 204 -- ls -la /var/opt/gitlab/backups/"
```

### Restore

```bash
# Stop services
ssh rawls "pct exec 204 -- gitlab-ctl stop puma"
ssh rawls "pct exec 204 -- gitlab-ctl stop sidekiq"

# Restore (replace TIMESTAMP with actual backup)
ssh rawls "pct exec 204 -- gitlab-backup restore BACKUP=TIMESTAMP"

# Reconfigure and restart
ssh rawls "pct exec 204 -- gitlab-ctl reconfigure"
ssh rawls "pct exec 204 -- gitlab-ctl restart"
```

### Proxmox Snapshots

Since GitLab runs in an LXC container, you can also use Proxmox snapshots:

```bash
# Create snapshot (from Rawls)
pct snapshot 204 pre-upgrade --description "Before GitLab upgrade"

# List snapshots
pct listsnapshot 204

# Rollback if needed
pct rollback 204 pre-upgrade
```

## Troubleshooting

### GitLab Won't Start

Check service status:
```bash
ssh rawls "pct exec 204 -- gitlab-ctl status"
```

Check logs:
```bash
ssh rawls "pct exec 204 -- gitlab-ctl tail"
```

### Out of Memory

GitLab needs at least 4GB RAM. Check usage:
```bash
ssh rawls "pct exec 204 -- free -h"
```

If low on memory, increase in `host_vars/rawls.yml`:
```yaml
gitlab_memory: 12288  # 12GB
```

Then resize container:
```bash
ssh rawls "pct set 204 -memory 12288"
```

### Container Won't Start

Check Proxmox logs:
```bash
ssh rawls "journalctl -u pve-container@204"
```

Verify container config:
```bash
ssh rawls "cat /etc/pve/lxc/204.conf"
```

### Health Check

```bash
ssh rawls "pct exec 204 -- gitlab-rake gitlab:check SANITIZE=true"
```

### Reset Root Password

```bash
ssh rawls "pct exec 204 -- gitlab-rake 'gitlab:password:reset[root]'"
```

## Updating GitLab

```bash
# Enter container
ssh rawls "pct enter 204"

# Update packages
apt-get update
apt-get install gitlab-ce

# GitLab will automatically reconfigure
```

For major upgrades, take a Proxmox snapshot first:
```bash
ssh rawls "pct snapshot 204 pre-upgrade"
```

## Files Created

| Path | Description |
|------|-------------|
| `ansible/roles/gitlab/` | Ansible role |
| `ansible/host_vars/rawls.yml` | Rawls configuration |
| `docs/gitlab-setup.md` | This documentation |
| `/root/gitlab-credentials.txt` | Password retrieval instructions (on Rawls) |

## Network Details

| Component | IP/Port | Description |
|-----------|---------|-------------|
| Rawls (Proxmox) | 10.203.3.47 | Host |
| GitLab (LXC) | 10.203.3.204 | Container |
| HTTP | :80 | Web interface |
| HTTPS | :443 | Secure web (if configured) |
| SSH | :22 | Git over SSH |

## Next Steps

1. [ ] Change root password (expires 24h after install)
2. [ ] Create personal admin account
3. [ ] Configure SSH key authentication
4. [ ] Mirror GitHub repositories (homelab-automation, dotfiles)
5. [ ] Set up CI/CD pipelines
6. [ ] Configure backup schedule
7. [ ] (Optional) Set up HTTPS with Let's Encrypt or self-signed cert
